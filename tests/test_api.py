"""
Tests for SentinelMesh REST API and Demo Launcher.
"""

import pytest
from starlette.testclient import TestClient
from backend.main import app
from backend.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] in ("healthy", "ok")


def test_create_and_list_projects():
    res = client.post("/api/projects", json={
        "name": "API Test Project",
        "code_snippet": "def hello(): return 'world'"
    })
    assert res.status_code in (200, 201)
    data = res.json()
    assert "id" in data
    assert data["name"] == "API Test Project"

    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_launch_demo_run():
    res = client.post("/api/demo/launch?llm_provider=offline")
    assert res.status_code in (200, 201)
    data = res.json()
    assert "project_id" in data
    assert "run_id" in data


def test_metrics_endpoint():
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "uptime_seconds" in data
    assert "total_requests" in data
    assert "active_runs" in data
    assert data["database_status"] == "online"


def test_trace_id_propagation():
    custom_trace = "test-custom-trace-id-12345"
    res = client.get("/api/health", headers={"X-Trace-ID": custom_trace})
    assert res.status_code == 200
    assert res.headers.get("X-Trace-ID") == custom_trace

