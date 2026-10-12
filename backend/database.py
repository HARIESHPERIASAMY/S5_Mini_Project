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
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "sentinelmesh.db"
DATABASE_URL = os.getenv("SENTINEL_DATABASE_URL", f"sqlite:///{DB_PATH}")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforces WAL mode, foreign keys, and 5000ms busy timeout."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA busy_timeout = 5000")
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA synchronous = NORMAL")
        cursor.close()


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionFactory)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database session."""
    db = ScopedSession()
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
