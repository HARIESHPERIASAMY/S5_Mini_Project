"""
Database setup for SentinelMesh using SQLAlchemy with SQLite.
Configures WAL mode, busy timeout, foreign key enforcement, and online backup.
"""

import os
import shutil
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "sentinelmesh.db"
_raw_db_url = os.getenv("SENTINEL_DATABASE_URL") or os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"

# Normalise Postgres dialect prefix if injected by hosting provider (Render, Railway, Heroku)
if _raw_db_url.startswith("postgres://"):
    _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)

DATABASE_URL = _raw_db_url
IS_SQLITE = DATABASE_URL.startswith("sqlite")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforces WAL mode, foreign keys, and 5000ms busy timeout on SQLite connections."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA busy_timeout = 5000")
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.close()


from sqlalchemy.pool import QueuePool

_connect_args = {"check_same_thread": False} if IS_SQLITE else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_timeout=15,
    pool_pre_ping=True
)

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database session."""
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session_scope():
    """Context manager for background tasks and agents."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def auto_migrate():
    """Applies schema migrations dynamically for SQLite tables."""
    if not IS_SQLITE:
        return
    from sqlalchemy import text
    try:
        with engine.begin() as conn:
            # Check columns in runs
            res = conn.execute(text("PRAGMA table_info(runs)")).fetchall()
            run_cols = {row[1] for row in res}
            if run_cols:
                if "idempotency_key" not in run_cols:
                    conn.execute(text("ALTER TABLE runs ADD COLUMN idempotency_key VARCHAR(255)"))
                if "trace_id" not in run_cols:
                    conn.execute(text("ALTER TABLE runs ADD COLUMN trace_id VARCHAR(64)"))
                if "failed_tests_count" not in run_cols:
                    conn.execute(text("ALTER TABLE runs ADD COLUMN failed_tests_count INTEGER DEFAULT 0"))
                if "agent_durations" not in run_cols:
                    conn.execute(text("ALTER TABLE runs ADD COLUMN agent_durations TEXT"))
                if "token_cost_usd" not in run_cols:
                    conn.execute(text("ALTER TABLE runs ADD COLUMN token_cost_usd FLOAT DEFAULT 0.0"))

            # Check columns in bugs
            res_bugs = conn.execute(text("PRAGMA table_info(bugs)")).fetchall()
            bug_cols = {row[1] for row in res_bugs}
            if bug_cols:
                if "workflow_state" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN workflow_state VARCHAR(50) DEFAULT 'open'"))
                if "dismiss_reason" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN dismiss_reason VARCHAR(255)"))
                if "assignee" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN assignee VARCHAR(100)"))
                if "tests_passed_after_fix" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN tests_passed_after_fix INTEGER"))
                if "tests_failed_after_fix" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN tests_failed_after_fix INTEGER"))
                if "regression_count" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN regression_count INTEGER DEFAULT 0"))
                if "critic_verdict" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN critic_verdict VARCHAR(50) DEFAULT 'NOT_REVIEWED'"))
                if "callers_count" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN callers_count INTEGER DEFAULT 0"))
                if "affected_callers" not in bug_cols:
                    conn.execute(text("ALTER TABLE bugs ADD COLUMN affected_callers TEXT"))

            # Check columns in agent_logs
            res_logs = conn.execute(text("PRAGMA table_info(agent_logs)")).fetchall()
            log_cols = {row[1] for row in res_logs}
            if log_cols and "seq" not in log_cols:
                conn.execute(text("ALTER TABLE agent_logs ADD COLUMN seq INTEGER"))
    except Exception:
        pass


def init_db():
    """Initialize database tables, run auto migrations, and recover interrupted runs."""
    import backend.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    auto_migrate()
    recover_interrupted_runs()



def recover_interrupted_runs():
    """Detects runs left in running/pending status across restarts and marks them INTERRUPTED."""
    from backend.models import Run
    try:
        with db_session_scope() as session:
            stuck_runs = session.query(Run).filter(Run.status.in_(["running", "pending"])).all()
            for r in stuck_runs:
                r.status = "interrupted"
                r.error_message = "Server restarted while analysis was in progress. You can retry this run."
    except Exception:
        pass


def backup_database(destination_path: Path) -> Path:
    """Performs a safe SQLite online backup."""
    if not IS_SQLITE:
        return destination_path
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    src_conn = sqlite3.connect(str(DB_PATH))
    dst_conn = sqlite3.connect(str(destination_path))
    try:
        src_conn.backup(dst_conn)
    finally:
        dst_conn.close()
        src_conn.close()
    return destination_path


def cleanup_temp_directories(max_age_seconds: int = 7200):
    """Cleans up temporary workspaces older than max_age_seconds."""
    projects_dir = DATA_DIR / "projects"
    if not projects_dir.exists():
        return
    now = time.time()
    for item in projects_dir.iterdir():
        if item.is_dir() and item.name.startswith(("sentinel_proj_", "sentinel_zip_", "sentinel_demo_")):
            try:
                mtime = item.stat().st_mtime
                if now - mtime > max_age_seconds:
                    shutil.rmtree(item, ignore_errors=True)
            except Exception:
                pass
