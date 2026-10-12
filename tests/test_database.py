"""
Unit tests for SentinelMesh database models and sessions.
"""

import pytest
from backend.database import Base, engine, db_session_scope, SessionFactory
from backend.models import Project, Run, Bug, FileRisk, TestResult, AgentLog, DebateMessage


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_create_project_and_run():
    with db_session_scope() as session:
        proj = Project(name="Test Project", source_type="snippet")
        session.add(proj)
        session.flush()

        run = Run(project_id=proj.id, status="pending", risk_score=42.5)
        session.add(run)
        session.flush()

        assert proj.id is not None
        assert run.id is not None
        assert run.risk_score == 42.5
        assert len(proj.runs) == 1


def test_create_bug_with_causal_chain():
    with db_session_scope() as session:
        proj = Project(name="Bug Test Project")
        session.add(proj)
        session.flush()

        run = Run(project_id=proj.id)
        session.add(run)
        session.flush()

        bug = Bug(
            run_id=run.id,
            file_path="billing.py",
            line_number=18,
            title="ZeroDivisionError",
            description="Division by zero",
            severity="CRITICAL",
            category="LOGIC",
            causal_chain='["step1", "step2"]',
            fix_verified=True
        )
        session.add(bug)
        session.flush()

        assert bug.id is not None
        assert bug.fix_verified is True
        assert bug.severity == "CRITICAL"
