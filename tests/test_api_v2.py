"""
Tests for SentinelMesh V2 Endpoints: Workflow, Impact Simulation, Run Compare,
Webhook Testing, and Project Health Trends.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import Base, engine, db_session_scope
from backend.models import Project, Run, Bug, TestResult

client = TestClient(app)


@pytest.fixture(autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_workflow_state_update():
    run_id = f"test_run_{uuid.uuid4().hex[:8]}"
    with db_session_scope() as session:
        proj = Project(name="Workflow Test Proj", source_type="snippet")
        session.add(proj)
        session.flush()

        run = Run(id=run_id, project_id=proj.id, status="completed", suite_health_score=80.0)
        session.add(run)

        bug = Bug(
            run_id=run_id,
            file_path="main.py",
            line_number=10,
            title="Division by Zero",
            description="Potential division by zero",
            severity="HIGH",
            category="arithmetic",
            confidence=0.95,
            workflow_state="open"
        )
        session.add(bug)
        session.flush()
        bug_id = bug.id

    # Test valid state update
    res = client.patch(f"/api/runs/{run_id}/bugs/{bug_id}/workflow", json={
        "workflow_state": "verified",
        "assignee": "alice@sentinelmesh.io"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["workflow_state"] == "verified"
    assert data["assignee"] == "alice@sentinelmesh.io"

    # Test dismissal with reason
    res2 = client.patch(f"/api/runs/{run_id}/bugs/{bug_id}/workflow", json={
        "workflow_state": "dismissed",
        "dismiss_reason": "False positive in dead code"
    })
    assert res2.status_code == 200
    assert res2.json()["workflow_state"] == "dismissed"
    assert res2.json()["dismiss_reason"] == "False positive in dead code"

    # Test invalid state
    res3 = client.patch(f"/api/runs/{run_id}/bugs/{bug_id}/workflow", json={
        "workflow_state": "invalid_custom_state"
    })
    assert res3.status_code == 400

    # Test non-existent bug
    res4 = client.patch(f"/api/runs/{run_id}/bugs/nonexistent/workflow", json={
        "workflow_state": "open"
    })
    assert res4.status_code == 404


def test_simulate_impact():
    run_id = f"test_run_{uuid.uuid4().hex[:8]}"
    with db_session_scope() as session:
        proj = Project(name="Simulate Test Proj", source_type="snippet")
        session.add(proj)
        session.flush()

        run = Run(id=run_id, project_id=proj.id, status="completed", suite_health_score=60.0, code_coverage=70.0)
        session.add(run)

        tr1 = TestResult(run_id=run_id, test_name="test_div", test_file="test_math.py", status="FAILED", duration_ms=12.0)
        tr2 = TestResult(run_id=run_id, test_name="test_mul", test_file="test_math.py", status="PASSED", duration_ms=10.0)
        session.add(tr1)
        session.add(tr2)

        bug = Bug(
            run_id=run_id,
            file_path="math.py",
            line_number=5,
            title="Zero Div",
            description="Division by zero error",
            severity="HIGH",
            category="arithmetic",
            confidence=0.9
        )
        session.add(bug)
        session.flush()
        bug_id = bug.id

    res = client.post(f"/api/runs/{run_id}/bugs/{bug_id}/simulate-impact")
    assert res.status_code == 200
    data = res.json()
    assert "current_score" in data
    assert "simulated_score" in data
    assert "score_delta" in data
    assert data["tests_fixed"] == 1
    assert data["score_delta"] > 0


def test_compare_runs():
    base_id = f"base_{uuid.uuid4().hex[:8]}"
    target_id = f"target_{uuid.uuid4().hex[:8]}"

    with db_session_scope() as session:
        proj = Project(name="Compare Test Proj", source_type="snippet")
        session.add(proj)
        session.flush()

        run1 = Run(id=base_id, project_id=proj.id, status="completed", suite_health_score=70.0, code_coverage=60.0)
        run2 = Run(id=target_id, project_id=proj.id, status="completed", suite_health_score=85.0, code_coverage=75.0)
        session.add(run1)
        session.add(run2)

        # Bug in base that is verified in target
        b1 = Bug(run_id=base_id, file_path="a.py", line_number=1, title="Bug A", description="Desc A", severity="HIGH", category="logic", confidence=0.9, deduplication_key="key_a", fix_verified=False)
        b2 = Bug(run_id=target_id, file_path="a.py", line_number=1, title="Bug A", description="Desc A", severity="HIGH", category="logic", confidence=0.9, deduplication_key="key_a", fix_verified=True)
        # New bug in target
        b3 = Bug(run_id=target_id, file_path="b.py", line_number=2, title="Bug B", description="Desc B", severity="MEDIUM", category="logic", confidence=0.8, deduplication_key="key_b", fix_verified=False)

        session.add_all([b1, b2, b3])

    res = client.get(f"/api/runs/compare?base_id={base_id}&target_id={target_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["score_delta"] == 15.0
    assert data["coverage_delta"] == 15.0
    assert len(data["fixed_bugs"]) >= 1
    assert len(data["new_bugs"]) >= 1


def test_webhook_test_endpoint():
    # Test invalid URL schema
    res = client.post("/api/integrations/webhook/test", json={"url": "ftp://example.com/webhook"})
    assert res.status_code == 200
    assert res.json()["success"] is False

    # Test unreachable dummy URL
    res2 = client.post("/api/integrations/webhook/test", json={"url": "http://127.0.0.1:59999/nonexistent"})
    assert res2.status_code == 200
    assert res2.json()["success"] is False


def test_project_health_trends():
    proj_id = None
    with db_session_scope() as session:
        proj = Project(name="Trends Test Proj", source_type="snippet")
        session.add(proj)
        session.flush()
        proj_id = proj.id

        run1 = Run(id=f"r1_{uuid.uuid4().hex[:6]}", project_id=proj.id, status="completed", suite_health_score=65.0)
        run2 = Run(id=f"r2_{uuid.uuid4().hex[:6]}", project_id=proj.id, status="completed", suite_health_score=80.0)
        session.add_all([run1, run2])

    res = client.get(f"/api/projects/{proj_id}/health-trends")
    assert res.status_code == 200
    data = res.json()
    assert data["project_id"] == proj_id
    assert len(data["points"]) == 2
    assert data["points"][0]["score"] == 65.0
    assert data["points"][1]["score"] == 80.0
