"""
Tests for Phase 3: Persistence and Recovery in SentinelMesh.
Verifies SQLite WAL pragmas, crash recovery of interrupted runs,
event-sourcing sequence numbering, backup export, and run pagination.
"""

import os
import sqlite3
import tempfile
from pathlib import Path
import pytest
from starlette.testclient import TestClient
from backend.main import app
from backend.database import (
    engine,
    db_session_scope,
    auto_migrate,
    recover_interrupted_runs,
    backup_database,
    cleanup_temp_directories,
    DB_PATH
)
from backend.models import Project, Run, AgentLog
from backend.event_bus import EventBus

client = TestClient(app)


def test_sqlite_pragmas_wal_mode():
    """Verify WAL mode, busy timeout, and foreign keys are active."""
    with engine.connect() as conn:
        res_wal = conn.exec_driver_sql("PRAGMA journal_mode").scalar()
        assert res_wal.lower() == "wal"

        res_timeout = conn.exec_driver_sql("PRAGMA busy_timeout").scalar()
        assert res_timeout == 5000

        res_fk = conn.exec_driver_sql("PRAGMA foreign_keys").scalar()
        assert res_fk == 1


def test_crash_recovery_marks_interrupted():
    """Verify that runs left in running/pending state across restarts become interrupted."""
    import uuid
    run_id = f"crash-run-{uuid.uuid4()}"
    with db_session_scope() as session:
        # Create a project and a fake running run
        proj = Project(name=f"Crash Test Proj {uuid.uuid4().hex[:6]}", source_type="snippet")
        session.add(proj)
        session.flush()

        fake_run = Run(id=run_id, project_id=proj.id, status="running")
        session.add(fake_run)

    # Trigger recovery function
    recover_interrupted_runs()

    # Verify run is marked interrupted
    with db_session_scope() as session:
        recovered = session.query(Run).filter(Run.id == run_id).first()
        assert recovered is not None
        assert recovered.status == "interrupted"
        assert "interrupted" in recovered.error_message.lower() or "restarted" in recovered.error_message.lower()


def test_event_sourcing_sequence_and_replay():
    """Verify sequential numbering and since_seq replay behavior in EventBus."""
    bus = EventBus()
    run_id = "event-test-run"

    class FakeWebSocket:
        def __init__(self):
            self.accepted = False
            self.messages = []

        async def accept(self):
            self.accepted = True

        async def send_text(self, text: str):
            self.messages.append(text)

    import asyncio

    async def _test():
        # Publish 5 events
        for i in range(5):
            await bus.publish(run_id, "log", "agent", {"message": f"Step {i}"})

        # Connect a client with since_seq = 2
        ws = FakeWebSocket()
        await bus.connect(run_id, ws, since_seq=2)

        # Should receive events 3, 4, 5 (3 events total)
        assert len(ws.messages) == 3
        import json
        seqs = [json.loads(m)["seq"] for m in ws.messages]
        assert seqs == [3, 4, 5]

    asyncio.run(_test())


def test_backup_database_endpoint():
    """Verify that database backup endpoint creates a valid SQLite database clone."""
    res = client.get("/api/backup")
    assert res.status_code == 200
    assert "sentinelmesh_backup" in res.headers.get("content-disposition", "")
    content = res.content
    assert len(content) > 0
    # SQLite files start with "SQLite format 3\000"
    assert content.startswith(b"SQLite format 3\000")


def test_paginated_runs_endpoint():
    """Verify pagination limit and offset parameters work correctly."""
    res = client.get("/api/runs?limit=3&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["limit"] == 3
    assert len(data["items"]) <= 3
