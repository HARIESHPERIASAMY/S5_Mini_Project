"""
Comprehensive Tests for Phase 7:
- Concurrency test (simultaneous parallel calls)
- Comprehensive endpoint coverage:
  - Project CRUD (create, get, list)
  - Run inspection (get, bugs, patch, report, logs, cancel, retry)
  - Backup binary download
  - EventBus publish and sequence replay (since_seq)
  - Invalid ID 404 error envelope handling
"""

import asyncio
import concurrent.futures
import uuid
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import db_session_scope
from backend.models import Project, Run, Bug, FileRisk
from backend.event_bus import EventBus

client = TestClient(app)


def test_concurrency_parallel_requests():
    """Verify system handles high-concurrency read requests simultaneously without database locks."""
    def make_request(i):
        return client.get("/api/health").status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 20
    assert all(code == 200 for code in results)


def test_project_get_endpoint():
    """Verify GET on /api/projects/{project_id}."""
    create_res = client.post("/api/projects", json={
        "name": f"CRUD Test {uuid.uuid4().hex[:6]}",
        "code_snippet": "def square(n): return n * n"
    })
    assert create_res.status_code == 201
    proj_id = create_res.json()["id"]

    get_res = client.get(f"/api/projects/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == proj_id


def test_run_detail_bugs_and_export_endpoints():
    """Verify run details, bugs listing, and report/patch generation endpoints."""
    run_id = f"test-run-{uuid.uuid4()}"
    with db_session_scope() as session:
        proj = Project(name=f"Run Export Proj {uuid.uuid4().hex[:6]}", source_type="snippet")
        session.add(proj)
        session.flush()

        run = Run(
            id=run_id,
            project_id=proj.id,
            status="completed",
            executive_summary="All tests passed successfully.",
            technical_report="# SentinelMesh Comprehensive Bug & Verification Report\n\nAll bugs remediated."
        )
        session.add(run)

        bug = Bug(
            run_id=run_id,
            title="ZeroDivision in divide",
            description="Literal division by zero detected in expression.",
            file_path="math_utils.py",
            line_number=12,
            severity="CRITICAL",
            category="LOGIC",
            proposed_fix_diff="--- a/math_utils.py\n+++ b/math_utils.py\n@@ -12 +12 @@\n- return a / 0\n+ return a if b == 0 else a / b"
        )
        session.add(bug)

    # 1. GET /api/runs/{run_id}
    res_run = client.get(f"/api/runs/{run_id}")
    assert res_run.status_code == 200
    data_run = res_run.json()
    assert data_run["id"] == run_id
    assert len(data_run["bugs"]) == 1

    # 2. GET /api/runs/{run_id}/patch
    res_patch = client.get(f"/api/runs/{run_id}/patch")
    assert res_patch.status_code == 200
    patch_text = res_patch.text
    assert "SentinelMesh Unified Fix Patch" in patch_text

    # 3. GET /api/runs/{run_id}/report
    res_report = client.get(f"/api/runs/{run_id}/report")
    assert res_report.status_code == 200
    report_data = res_report.json()
    assert report_data["run_id"] == run_id

    res_report_html = client.get(f"/api/runs/{run_id}/report?format=html")
    assert res_report_html.status_code == 200
    assert "SentinelMesh Comprehensive Bug & Verification Report" in res_report_html.text

    # 4. GET /api/runs/{run_id}/logs
    res_logs = client.get(f"/api/runs/{run_id}/logs")
    assert res_logs.status_code == 200


def test_run_cancel_and_retry_endpoints():
    """Verify cancelling an active run and retrying a run."""
    run_id = f"cancel-retry-{uuid.uuid4()}"
    with db_session_scope() as session:
        proj = Project(name=f"Cancel Proj {uuid.uuid4().hex[:6]}", source_type="snippet")
        session.add(proj)
        session.flush()

        run = Run(id=run_id, project_id=proj.id, status="running")
        session.add(run)

    # 1. Cancel
    res_cancel = client.post(f"/api/runs/{run_id}/cancel")
    assert res_cancel.status_code == 200
    assert res_cancel.json()["success"] is True

    # Check status changed
    res_detail = client.get(f"/api/runs/{run_id}")
    assert res_detail.json()["status"] == "cancelled"

    # 2. Retry
    res_retry = client.post(f"/api/runs/{run_id}/retry?llm_provider=offline")
    assert res_retry.status_code in (200, 201)
    assert "run_id" in res_retry.json()


def test_backup_database_endpoint():
    """Verify GET /api/backup exports a valid SQLite binary stream."""
    res = client.get("/api/backup")
    assert res.status_code == 200
    assert res.headers["content-type"] in ("application/octet-stream", "application/x-sqlite3")
    assert res.content[:16] == b"SQLite format 3\x00"


@pytest.mark.asyncio
async def test_event_bus_publish_and_replay():
    """Verify EventBus publishes events, increments seq, and handles replay."""
    eb = EventBus()

    await eb.publish("run-replay-101", "log", agent_name="orchestrator", data={"text": "Step 1"})
    await eb.publish("run-replay-101", "log", agent_name="orchestrator", data={"text": "Step 2"})

    # Test replay since seq 1
    replayed = eb.get_history_since("run-replay-101", since_seq=1)
    assert len(replayed) == 1
    assert replayed[0]["seq"] == 2
    assert replayed[0]["data"]["text"] == "Step 2"

    eb.clear_run("run-replay-101")
    assert len(eb.get_history_since("run-replay-101")) == 0


def test_invalid_endpoints_and_resources_404():
    """Verify non-existent endpoints and IDs return proper 404 envelopes."""
    res1 = client.get("/api/non-existent-endpoint")
    assert res1.status_code == 404
    assert res1.json()["error"] == "NotFoundError"

    res2 = client.get(f"/api/projects/{uuid.uuid4()}")
    assert res2.status_code == 404
    assert res2.json()["error"] == "NotFoundError"

    res3 = client.get(f"/api/runs/{uuid.uuid4()}")
    assert res3.status_code == 404
    assert res3.json()["error"] == "NotFoundError"


def test_create_run_and_idempotency_workflow():
    """Verify POST /api/runs creation, idempotency, and project filtering."""
    # 1. Create project
    p_res = client.post("/api/projects", json={
        "name": f"Workflow Project {uuid.uuid4().hex[:6]}",
        "code_snippet": "def multiply(a, b): return a * b"
    })
    proj_id = p_res.json()["id"]

    # 2. Start run with idempotency key
    idem_key = f"idem-{uuid.uuid4()}"
    run_res1 = client.post("/api/runs", json={
        "project_id": proj_id,
        "llm_provider": "offline",
        "idempotency_key": idem_key
    })
    assert run_res1.status_code in (200, 201)
    run_id = run_res1.json()["run_id"]

    # 3. Idempotent call with duplicate key
    run_res2 = client.post("/api/runs", json={
        "project_id": proj_id,
        "llm_provider": "offline",
        "idempotency_key": idem_key
    })
    assert run_res2.status_code in (200, 201, 409)

    # 4. List runs filtered by project_id
    list_runs = client.get(f"/api/runs?project_id={proj_id}&limit=10&offset=0")
    assert list_runs.status_code == 200
    data = list_runs.json()
    assert "items" in data
    assert len(data["items"]) >= 1

