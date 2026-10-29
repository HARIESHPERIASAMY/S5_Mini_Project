"""
FastAPI Main Application for SentinelMesh.
Production-hardened gateway featuring global exception handlers, strict validation,
idempotency, cancellation, metrics, database backup, and event-sourced WebSocket streaming.
"""

import asyncio
from datetime import datetime, timezone
import io
from pathlib import Path
import shutil
import tempfile
import time
import uuid
import zipfile
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

from fastapi import (
    FastAPI, Depends, HTTPException, UploadFile, File, WebSocket,
    WebSocketDisconnect, Request, Query, status
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import (
    get_db, init_db, db_session_scope, backup_database,
    cleanup_temp_directories, DB_PATH
)
from backend.models import Project, Run, Bug, FileRisk, TestResult, MutationRecord, DebateMessage, AgentLog
from backend.schemas import (
    ProjectCreate, ProjectResponse,
    RunResponse, RunDetailResponse, PaginatedRunsResponse,
    StartRunRequest, ActionResponse, MetricsResponse,
    StandardErrorResponse,
    BugResponse, BugWorkflowUpdate,
    ImpactSimulationResponse, RunComparisonResponse,
    WebhookTestRequest, WebhookTestResponse,
    HealthTrendsResponse, HealthTrendPoint
)
from backend.event_bus import bus
from backend.llm import get_llm_provider
from agents.orchestrator_agent import OrchestratorAgent
from sandbox.runner import default_runner

BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "demo" / "ecommerce"
PROJECTS_DIR = BASE_DIR / "data" / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# Performance & Metric Counters
SERVER_START_TIME = time.time()
METRICS = {
    "total_requests": 0,
    "latencies": [],
    "active_runs": set(),
}
RUN_TASKS: Dict[str, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables, enable WAL, crash recovery
    init_db()
    cleanup_temp_directories()
    yield
    # Shutdown: terminate any active subprocesses
    for run_id in list(RUN_TASKS.keys()):
        default_runner.terminate_run_processes(run_id)


app = FastAPI(
    title="SentinelMesh API",
    description="Intelligent Multi-Agent Software Testing and Bug Analysis Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Enable GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global Telemetry, Structured Logging & Rate Limiting Middleware
# ---------------------------------------------------------------------------

import logging

logger = logging.getLogger("sentinelmesh")
if not logger.handlers:
    _log_handler = logging.StreamHandler()
    _log_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s"))
    logger.addHandler(_log_handler)
    logger.setLevel(logging.INFO)

RATE_LIMIT_STORE: Dict[str, List[float]] = {}
RATE_LIMIT_MAX_PER_MINUTE = 600

@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    request.state.trace_id = trace_id

    # Rate Limiting Guard
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    req_history = [t for t in RATE_LIMIT_STORE.get(client_ip, []) if now - t < 60.0]
    if len(req_history) >= RATE_LIMIT_MAX_PER_MINUTE:
        logger.warning(f"[{trace_id}] 429 RateLimitExceeded for client {client_ip} on {request.url.path}")
        return create_error_response("RateLimitExceeded", "Too many requests. Rate limit exceeded (max 600 req/min).", 429, trace_id)
    req_history.append(now)
    RATE_LIMIT_STORE[client_ip] = req_history

    start = time.perf_counter()
    METRICS["total_requests"] += 1

    response = await call_next(request)

    latency_ms = (time.perf_counter() - start) * 1000.0
    METRICS["latencies"].append(latency_ms)
    if len(METRICS["latencies"]) > 1000:
        METRICS["latencies"] = METRICS["latencies"][-1000:]

    response.headers["X-Trace-ID"] = trace_id
    logger.info(f"[{trace_id}] {request.method} {request.url.path} -> {response.status_code} ({latency_ms:.2f}ms)")

    # If an /api/ route returned 404 (e.g. from static handler), format as standard JSON
    if response.status_code == 404 and request.url.path.startswith("/api/"):
        return create_error_response("NotFoundError", f"API endpoint '{request.url.path}' does not exist.", 404, trace_id)

    return response



# ---------------------------------------------------------------------------
# Global Standardized JSON Exception Handlers
# ---------------------------------------------------------------------------

def create_error_response(error_code: str, detail: Any, status_code: int, trace_id: str) -> JSONResponse:
    payload = {
        "error": error_code,
        "detail": detail,
        "trace_id": trace_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return JSONResponse(status_code=status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    formatted_errors = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", [])])
        formatted_errors.append(f"{loc}: {err.get('msg', 'Validation error')}")
    detail_msg = "; ".join(formatted_errors) if formatted_errors else "Invalid request payload format."
    return create_error_response("ValidationError", detail_msg, status.HTTP_422_UNPROCESSABLE_ENTITY, trace_id)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    err_code = "NotFoundError" if exc.status_code == 404 else ("MethodNotAllowed" if exc.status_code == 405 else "HTTPError")
    return create_error_response(err_code, exc.detail, exc.status_code, trace_id)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    return create_error_response("InternalServerError", f"An unexpected error occurred: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR, trace_id)


# ---------------------------------------------------------------------------
# Health & Metrics Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """Verifies service liveness and database connection integrity."""
    start_db = time.perf_counter()
    try:
        db.execute(text("SELECT 1")).scalar()
        db_ok = True
        db_latency_ms = round((time.perf_counter() - start_db) * 1000.0, 2)
    except Exception as e:
        db_ok = False
        db_latency_ms = -1.0

    return {
        "status": "healthy" if db_ok else "degraded",
        "platform": "SentinelMesh",
        "version": "1.0.0",
        "database": {"connected": db_ok, "latency_ms": db_latency_ms},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/metrics", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    """Provides operational observability and throughput statistics."""
    uptime = round(time.time() - SERVER_START_TIME, 1)
    avg_latency = round(sum(METRICS["latencies"]) / len(METRICS["latencies"]), 2) if METRICS["latencies"] else 0.0

    try:
        completed_runs = db.query(Run).filter(Run.status == "completed").count()
        failed_runs = db.query(Run).filter(Run.status == "failed").count()
        interrupted_runs = db.query(Run).filter(Run.status == "interrupted").count()
    except Exception:
        completed_runs = 0
        failed_runs = 0
        interrupted_runs = 0

    return MetricsResponse(
        uptime_seconds=uptime,
        total_requests=METRICS["total_requests"],
        active_runs=len(METRICS["active_runs"]),
        completed_runs=completed_runs,
        failed_runs=failed_runs,
        interrupted_runs=interrupted_runs,
        avg_latency_ms=avg_latency,
        database_status="online"
    )


# ---------------------------------------------------------------------------
# Project Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """Creates a project from a validated Python snippet or configuration."""
    proj_dir = tempfile.mkdtemp(prefix="sentinel_proj_", dir=PROJECTS_DIR)

    if payload.code_snippet:
        snippet_file = Path(proj_dir) / "main.py"
        snippet_file.write_text(payload.code_snippet, encoding="utf-8")

    project = Project(
        name=payload.name,
        description=payload.description or "Source code project",
        source_type=payload.source_type,
        source_path=proj_dir
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.post("/api/projects/upload", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def upload_project_zip(
    name: str = Query(..., min_length=1, max_length=100),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Securely uploads and extracts a project archive with zip-slip and zip-bomb protection.
    """
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Invalid archive format. Only .zip archives are supported.")

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:  # 20 MB compressed limit
        raise HTTPException(status_code=413, detail="Archive exceeds maximum allowed size limit of 20MB.")

    proj_dir = Path(tempfile.mkdtemp(prefix="sentinel_zip_", dir=PROJECTS_DIR))
    total_uncompressed = 0
    file_count = 0

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            for info in zf.infolist():
                file_count += 1
                if file_count > 500:
                    raise HTTPException(status_code=400, detail="Archive contains too many files (max 500 allowed).")

                # Reject symlinks (bitmask 0o120000)
                if (info.external_attr >> 16) & 0o120000 == 0o120000:
                    raise HTTPException(status_code=400, detail="Archive contains unsafe symlinks.")

                total_uncompressed += info.file_size
                if total_uncompressed > 50 * 1024 * 1024:  # 50 MB uncompressed limit
                    raise HTTPException(status_code=413, detail="Extracted archive size exceeds safe limits (max 50MB).")

                # Zip-bomb compression ratio check (>100:1)
                if len(content) > 0 and (total_uncompressed / max(len(content), 1)) > 100:
                    raise HTTPException(status_code=400, detail="Zip-bomb detected: compression ratio exceeds 100:1.")

                # Zip-Slip Guard
                target_path = (proj_dir / info.filename).resolve()
                try:
                    target_path.relative_to(proj_dir.resolve())
                except ValueError:
                    raise HTTPException(status_code=400, detail="Zip-slip path traversal attempt detected.")
                if not str(target_path).startswith(str(proj_dir.resolve())) or ".." in Path(info.filename).parts:
                    raise HTTPException(status_code=400, detail="Zip-slip path traversal attempt detected.")

            # Safe extraction
            zf.extractall(proj_dir)

    except HTTPException:
        shutil.rmtree(proj_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(proj_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"Corrupt or invalid zip archive: {str(e)}")

    project = Project(
        name=name.strip(),
        description=f"Uploaded ZIP: {file.filename}",
        source_type="zip",
        source_path=str(proj_dir)
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@app.get("/api/projects", response_model=List[ProjectResponse])
def list_projects(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return db.query(Project).order_by(Project.created_at.desc()).offset(offset).limit(limit).all()


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")
    return proj


# ---------------------------------------------------------------------------
# Demo Project Quick-Launch
# ---------------------------------------------------------------------------

@app.post("/api/demo/launch", status_code=status.HTTP_201_CREATED)
async def launch_demo_run(
    llm_provider: str = Query("offline", pattern=r"^(offline|gemini|openai|ollama)$"),
    db: Session = Depends(get_db)
):
    """
    1-Click Demo Launcher: Clones demo microservice and launches swarm analysis.
    """
    proj_dir = Path(tempfile.mkdtemp(prefix="sentinel_demo_", dir=PROJECTS_DIR))
    if DEMO_DIR.exists():
        shutil.copytree(str(DEMO_DIR), str(proj_dir), dirs_exist_ok=True)
    else:
        proj_dir.mkdir(parents=True, exist_ok=True)
        (proj_dir / "sample.py").write_text("def div(a, b): return a / b\n", encoding="utf-8")

    project = Project(
        name="FinTech E-Commerce Microservice (Demo)",
        description="Pre-seeded buggy project featuring division-by-zero, SQL injection, off-by-one, and null dereference.",
        source_type="demo",
        source_path=str(proj_dir)
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    run = Run(
        project_id=project.id,
        status="pending",
        current_agent="orchestrator",
        progress_pct=0
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Launch background task on running asyncio event loop
    task = asyncio.create_task(_execute_run_pipeline(run.id, str(proj_dir), llm_provider))
    RUN_TASKS[run.id] = task

    return {
        "project_id": project.id,
        "run_id": run.id,
        "message": "Demo project initialized and multi-agent analysis launched."
    }


# ---------------------------------------------------------------------------
# Run Lifecycle Endpoints (Idempotency, Pagination, Cancellation, Retry)
# ---------------------------------------------------------------------------

@app.post("/api/runs", status_code=status.HTTP_201_CREATED)
async def start_run(payload: StartRunRequest, db: Session = Depends(get_db)):
    """
    Starts an analysis run with in-flight lock and idempotency protection.
    """
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # In-flight lock: Prevent double-clicking starting duplicate concurrent runs for same project
    active_run = db.query(Run).filter(
        Run.project_id == payload.project_id,
        Run.status.in_(["running", "pending"])
    ).first()
    if active_run:
        raise HTTPException(
            status_code=409,
            detail=f"An analysis run ({active_run.id}) is already currently active for this project."
        )

    # Idempotency Key check
    if payload.idempotency_key:
        existing = db.query(Run).filter(Run.idempotency_key == payload.idempotency_key).first()
        if existing:
            return {"run_id": existing.id, "status": existing.status, "idempotent_replay": True}

    run = Run(
        project_id=project.id,
        idempotency_key=payload.idempotency_key,
        status="pending",
        current_agent="orchestrator",
        progress_pct=0
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    task = asyncio.create_task(_execute_run_pipeline(run.id, project.source_path, payload.llm_provider))
    RUN_TASKS[run.id] = task

    return {"run_id": run.id, "status": "pending"}


@app.get("/api/runs", response_model=PaginatedRunsResponse)
def list_runs(
    project_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Run)
    if project_id:
        query = query.filter(Run.project_id == project_id)
    if status_filter:
        query = query.filter(Run.status == status_filter)

    total = query.count()
    items = query.order_by(Run.started_at.desc()).offset(offset).limit(limit).all()

    return PaginatedRunsResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@app.get("/api/runs/compare", response_model=RunComparisonResponse)
def compare_runs(
    base_id: str = Query(..., description="Baseline run ID"),
    target_id: str = Query(..., description="Target or candidate run ID"),
    db: Session = Depends(get_db)
):
    """Compares two pipeline runs, identifying fixed, new, and unchanged bugs."""
    base_run = db.query(Run).filter(Run.id == base_id).first()
    if not base_run:
        raise HTTPException(status_code=404, detail=f"Base run '{base_id}' not found")
    target_run = db.query(Run).filter(Run.id == target_id).first()
    if not target_run:
        raise HTTPException(status_code=404, detail=f"Target run '{target_id}' not found")

    score_delta = round(float(target_run.suite_health_score or 0.0) - float(base_run.suite_health_score or 0.0), 1)
    coverage_delta = round(float(target_run.code_coverage or 0.0) - float(base_run.code_coverage or 0.0), 1)

    base_bugs = base_run.bugs or []
    target_bugs = target_run.bugs or []

    def make_key(b):
        return b.deduplication_key or f"{b.file_path}:{b.line_number}:{b.bug_type or b.title}"

    base_keys = {make_key(b): b for b in base_bugs}
    target_keys = {make_key(b): b for b in target_bugs}

    fixed = [b for k, b in base_keys.items() if k not in target_keys or getattr(target_keys[k], "fix_verified", False)]
    new = [b for k, b in target_keys.items() if k not in base_keys]
    unchanged = [b for k, b in target_keys.items() if k in base_keys and not getattr(b, "fix_verified", False)]

    return RunComparisonResponse(
        base_run_id=base_id,
        target_run_id=target_id,
        score_delta=score_delta,
        coverage_delta=coverage_delta,
        fixed_bugs=fixed,
        new_bugs=new,
        unchanged_bugs=unchanged
    )


@app.get("/api/runs/{run_id}", response_model=RunDetailResponse)
def get_run_details(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run


@app.post("/api/runs/{run_id}/cancel", response_model=ActionResponse)
async def cancel_run(run_id: str, db: Session = Depends(get_db)):
    """
    Cancels an active run, terminates any spawned sandbox subprocesses,
    and transitions state to cancelled.
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    if run.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel run with terminal status '{run.status}'.")

    # 1. Terminate all sandbox subprocesses
    default_runner.terminate_run_processes(run_id)

    # 2. Cancel the asyncio task if still scheduled
    task = RUN_TASKS.get(run_id)
    if task and not task.done():
        task.cancel()

    # 3. Update database record
    run.status = "cancelled"
    run.completed_at = datetime.now(timezone.utc)
    run.error_message = "Execution cancelled by user request."
    db.commit()

    if run_id in METRICS["active_runs"]:
        METRICS["active_runs"].remove(run_id)

    await bus.publish(
        run_id=run_id,
        event_type="run_status",
        agent_name="orchestrator",
        data={"status": "cancelled", "message": "Run cancelled by user request."},
        level="WARN"
    )

    return ActionResponse(success=True, message="Run cancelled successfully.", run_id=run_id)


@app.post("/api/runs/{run_id}/retry", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def retry_run(run_id: str, db: Session = Depends(get_db)):
    """
    Retries an interrupted or failed run.
    """
    old_run = db.query(Run).filter(Run.id == run_id).first()
    if not old_run:
        raise HTTPException(status_code=404, detail="Run not found.")

    project = db.query(Project).filter(Project.id == old_run.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Associated project not found.")

    new_run = Run(
        project_id=project.id,
        status="pending",
        current_agent="orchestrator",
        progress_pct=0
    )
    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    task = asyncio.create_task(_execute_run_pipeline(new_run.id, project.source_path, "offline"))
    RUN_TASKS[new_run.id] = task

    return ActionResponse(
        success=True,
        message="Retry run scheduled successfully.",
        run_id=new_run.id
    )


@app.get("/api/runs/{run_id}/logs")
def get_run_logs(
    run_id: str,
    since_seq: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """Event-sourced sequence log lookup supporting delta replay."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    query = db.query(AgentLog).filter(AgentLog.run_id == run_id)
    if since_seq is not None:
        query = query.filter(AgentLog.seq > since_seq)
    return query.order_by(AgentLog.seq.asc()).all()


@app.get("/api/runs/{run_id}/patch", response_class=PlainTextResponse)
def download_patch(run_id: str, db: Session = Depends(get_db)):
    """Export unified diff patch for all verified bugs."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    diff_lines = [
        f"# SentinelMesh Unified Fix Patch",
        f"# Run ID: {run_id}",
        f"# Generated: {run.completed_at or 'In Progress'}",
        "#" * 60,
        ""
    ]

    for bug in run.bugs:
        if bug.proposed_fix_diff:
            diff_lines.append(f"# Bug: {bug.title} ({'VERIFIED' if bug.fix_verified else 'PROPOSED'})")
            diff_lines.append(bug.proposed_fix_diff)
            diff_lines.append("")

    return "\n".join(diff_lines)


@app.get("/api/runs/{run_id}/report")
def get_report(
    run_id: str,
    format: str = Query("json", pattern=r"^(json|html|md|markdown)$"),
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")

    if format.lower() in ("md", "markdown"):
        return PlainTextResponse(run.technical_report or "No report generated yet.")
    elif format.lower() == "html":
        md_content = run.technical_report or "No report available."
        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SentinelMesh Audit Report - {run_id}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; line-height: 1.6; max-width: 900px; margin: 0 auto; }}
    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
    th, td {{ border: 1px solid #334155; padding: 10px 14px; text-align: left; }}
    th {{ background: #1e293b; color: #38bdf8; }}
    code {{ background: #1e293b; color: #a5f3fc; padding: 2px 6px; border-radius: 4px; }}
    h1, h2, h3 {{ color: #38bdf8; }}
    hr {{ border: 0; border-top: 1px solid #334155; margin: 30px 0; }}
  </style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">{md_content}</pre>
</body>
</html>"""
        return PlainTextResponse(html, media_type="text/html")

    return {
        "run_id": run.id,
        "summary": run.executive_summary,
        "metrics": {
            "total_files": run.total_files,
            "loc": run.lines_of_code,
            "risk_score": run.risk_score,
            "code_coverage": run.code_coverage,
            "mutation_score": run.mutation_score,
            "suite_health_score": run.suite_health_score,
            "bugs_count": run.bugs_count,
            "fixes_verified_count": run.fixes_verified_count
        },
        "technical_report": run.technical_report
    }


# ---------------------------------------------------------------------------
# V2 Workflow, Comparison, Simulation, and Integration Endpoints
# ---------------------------------------------------------------------------

@app.patch("/api/runs/{run_id}/bugs/{bug_id}/workflow", response_model=BugResponse)
async def update_bug_workflow(
    run_id: str,
    bug_id: str,
    payload: BugWorkflowUpdate,
    db: Session = Depends(get_db)
):
    """Updates bug triage and merge-readiness workflow state and broadcasts update."""
    bug = db.query(Bug).filter(Bug.id == bug_id, Bug.run_id == run_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail=f"Bug '{bug_id}' not found for run '{run_id}'")

    valid_states = {"open", "fix_proposed", "verified", "pr_opened", "merged", "dismissed"}
    if payload.workflow_state not in valid_states:
        raise HTTPException(status_code=400, detail=f"Invalid workflow state. Must be one of {sorted(valid_states)}")

    bug.workflow_state = payload.workflow_state
    if payload.dismiss_reason is not None:
        bug.dismiss_reason = payload.dismiss_reason
    if payload.assignee is not None:
        bug.assignee = payload.assignee

    db.commit()
    db.refresh(bug)

    # Broadcast real-time event to connected UI clients
    await bus.publish(
        run_id=run_id,
        event_type="bug_workflow_updated",
        agent_name="workflow",
        data={
            "bug_id": bug.id,
            "workflow_state": bug.workflow_state,
            "dismiss_reason": bug.dismiss_reason,
            "assignee": bug.assignee
        }
    )
    return bug


@app.post("/api/runs/{run_id}/bugs/{bug_id}/simulate-impact", response_model=ImpactSimulationResponse)
def simulate_bug_fix_impact(
    run_id: str,
    bug_id: str,
    db: Session = Depends(get_db)
):
    """Calculates authoritative health score and coverage delta if the bug fix is merged."""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    bug = db.query(Bug).filter(Bug.id == bug_id, Bug.run_id == run_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    test_results = run.test_results or []
    total_tests = len(test_results)
    passed_count = sum(1 for t in test_results if str(getattr(t, "status", "")).upper() == "PASSED")
    failed_count = sum(1 for t in test_results if str(getattr(t, "status", "")).upper() == "FAILED")
    flaky_count = sum(1 for t in test_results if getattr(t, "is_flaky", False))
    flaky_penalty = min(25.0, flaky_count * 10.0)

    current_cov = float(run.code_coverage or 0.0)
    current_score = float(run.suite_health_score or 0.0)

    # If this bug has failed tests or unverified state, simulate 1 test fix & modest coverage gain
    tests_fixed = 1 if (failed_count > 0 or not bug.fix_verified) else 0
    sim_passed = min(total_tests, passed_count + tests_fixed) if total_tests > 0 else (passed_count + tests_fixed)
    sim_total = max(1, total_tests)
    sim_pass_rate = (sim_passed / sim_total * 100.0) if sim_total > 0 else 100.0
    sim_cov = min(100.0, current_cov + (1.5 if tests_fixed > 0 else 0.0))

    sim_score = round(max(0.0, min(100.0, (sim_pass_rate * 0.5) + (sim_cov * 0.5) - flaky_penalty)), 1)
    score_delta = round(sim_score - current_score, 1)
    cov_delta = round(sim_cov - current_cov, 1)

    return ImpactSimulationResponse(
        current_score=current_score,
        simulated_score=sim_score,
        score_delta=score_delta,
        current_coverage=current_cov,
        simulated_coverage=sim_cov,
        coverage_delta=cov_delta,
        tests_fixed=tests_fixed,
        regression_risk="LOW" if (bug.regression_count or 0) == 0 else "MEDIUM"
    )


@app.post("/api/integrations/webhook/test", response_model=WebhookTestResponse)
def test_webhook_endpoint(payload: WebhookTestRequest):
    """Safely pings an external webhook endpoint with a 5s timeout."""
    import urllib.request
    import urllib.error
    import json

    if not payload.url.startswith(("http://", "https://")):
        return WebhookTestResponse(
            success=False,
            status_code=None,
            message="Invalid webhook URL. Must start with http:// or https://"
        )

    try:
        body = json.dumps({
            "event": "sentinelmesh.ping",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "SentinelMesh Test Runner"
        }).encode("utf-8")

        req = urllib.request.Request(
            payload.url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "SentinelMesh-Webhook-Tester/1.0"
            },
            method="POST"
        )
        if payload.secret:
            req.add_header("X-SentinelMesh-Secret", payload.secret)

        with urllib.request.urlopen(req, timeout=5.0) as resp:
            status_code = resp.getcode()
            success = 200 <= status_code < 300
            return WebhookTestResponse(
                success=success,
                status_code=status_code,
                message=f"Webhook responded with HTTP {status_code}"
            )
    except urllib.error.HTTPError as he:
        return WebhookTestResponse(
            success=False,
            status_code=he.code,
            message=f"HTTP Error {he.code}: {he.reason}"
        )
    except Exception as ex:
        return WebhookTestResponse(
            success=False,
            status_code=None,
            message=f"Connection failed: {str(ex)}"
        )


@app.get("/api/projects/{project_id}/health-trends", response_model=HealthTrendsResponse)
def get_project_health_trends(project_id: str, db: Session = Depends(get_db)):
    """Returns chronological run health scores for historical trend rendering."""
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    runs = db.query(Run).filter(Run.project_id == project_id).order_by(Run.started_at.asc()).all()
    points = [
        HealthTrendPoint(
            run_id=r.id,
            score=float(r.suite_health_score or 0.0),
            created_at=r.started_at or datetime.now(timezone.utc)
        )
        for r in runs
    ]
    return HealthTrendsResponse(project_id=project_id, points=points)


# ---------------------------------------------------------------------------
# Database Backup Export Endpoint
# ---------------------------------------------------------------------------

@app.get("/api/backup")
def export_database_backup():
    """Performs an online WAL backup of the SQLite database and streams it."""
    temp_backup = Path(tempfile.gettempdir()) / f"sentinelmesh_backup_{int(time.time())}.db"
    backup_database(temp_backup)

    def iterfile():
        try:
            with open(temp_backup, "rb") as f:
                while chunk := f.read(64 * 1024):
                    yield chunk
        finally:
            if temp_backup.exists():
                temp_backup.unlink(missing_ok=True)

    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=sentinelmesh_backup.db"}
    )


# ---------------------------------------------------------------------------
# WebSocket Endpoint with Event Replay
# ---------------------------------------------------------------------------

@app.websocket("/ws/runs/{run_id}")
async def websocket_run_stream(
    websocket: WebSocket,
    run_id: str,
    since_seq: Optional[int] = Query(None)
):
    await bus.connect(run_id, websocket, since_seq=since_seq)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await bus.disconnect(run_id, websocket)
    except Exception:
        await bus.disconnect(run_id, websocket)


# ---------------------------------------------------------------------------
# Internal Background Pipeline Execution
# ---------------------------------------------------------------------------

async def _execute_run_pipeline(run_id: str, workspace_dir: str, llm_provider_name: str = "offline"):
    METRICS["active_runs"].add(run_id)
    try:
        llm = get_llm_provider(llm_provider_name)
        orchestrator = OrchestratorAgent(llm)
        await orchestrator.execute_run(run_id, workspace_dir)
    except Exception as e:
        pass
    finally:
        if run_id in METRICS["active_runs"]:
            METRICS["active_runs"].remove(run_id)
        if run_id in RUN_TASKS:
            del RUN_TASKS[run_id]





# ---------------------------------------------------------------------------
# Mount Built Frontend Static Assets
# ---------------------------------------------------------------------------

FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
