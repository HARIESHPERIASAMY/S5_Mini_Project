"""
Tests for SentinelMesh Multi-Agent Swarm and Orchestration.
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest

from backend.llm.offline_provider import OfflineLLMProvider
from agents.static_analysis_agent import StaticAnalysisAgent
from agents.test_generation_agent import TestGenerationAgent
from agents.bug_classification_agent import BugClassificationAgent
from agents.root_cause_agent import RootCauseAgent
from agents.critic_agent import CriticAgent
from agents.report_agent import ReportAgent
from agents.orchestrator_agent import OrchestratorAgent
from backend.database import db_session_scope, Base, engine
from backend.models import Project, Run


@pytest.fixture(autouse=True)
def init_db_fixture():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.mark.asyncio
async def test_static_analysis_agent():
    llm = OfflineLLMProvider()
    agent = StaticAnalysisAgent(llm)

    demo_dir = Path(__file__).resolve().parent.parent / "demo" / "ecommerce"
    with db_session_scope() as session:
        proj = Project(name="Agent Test Proj")
        session.add(proj)
        session.flush()
        run = Run(project_id=proj.id)
        session.add(run)
        session.flush()
        run_id = run.id

    res = await agent.run(run_id, {"workspace_dir": str(demo_dir)})
    assert "file_risks" in res
    assert len(res["file_risks"]) >= 3
    # Check that risks were detected
    assert res["avg_risk"] > 0


@pytest.mark.asyncio
async def test_critic_agent_debate():
    llm = OfflineLLMProvider()
    critic = CriticAgent(llm)

    with db_session_scope() as session:
        proj = Project(name="Critic Test")
        session.add(proj)
        session.flush()
        run = Run(project_id=proj.id)
        session.add(run)
        session.flush()
        run_id = run.id

    bugs = [
        {"id": "b1", "title": "ZeroDivisionError", "severity": "CRITICAL", "fix_verified": True},
        {"id": "b2", "title": "SQL Injection", "severity": "HIGH", "fix_verified": False}
    ]

    res = await critic.run(run_id, {"bugs": bugs})
    assert "overall_consensus" in res
    assert res["overall_consensus"] >= 80.0


@pytest.mark.asyncio
async def test_orchestrator_end_to_end_on_demo():
    llm = OfflineLLMProvider()
    orchestrator = OrchestratorAgent(llm)

    demo_dir = Path(__file__).resolve().parent.parent / "demo" / "ecommerce"
    # Create isolated copy of demo workspace for test run
    with tempfile.TemporaryDirectory() as tmp_workspace:
        shutil.copytree(str(demo_dir), tmp_workspace, dirs_exist_ok=True)

        with db_session_scope() as session:
            proj = Project(name="E2E Demo Run", source_path=tmp_workspace)
            session.add(proj)
            session.flush()
            run = Run(project_id=proj.id)
            session.add(run)
            session.flush()
            run_id = run.id

        result = await orchestrator.execute_run(run_id, tmp_workspace)
        assert result is not None

        # Verify DB final state
        with db_session_scope() as session:
            db_run = session.query(Run).filter(Run.id == run_id).first()
            assert db_run is not None
            assert db_run.status == "completed"
            assert db_run.progress_pct == 100
            assert db_run.bugs_count > 0
            assert db_run.code_coverage > 0
            assert db_run.executive_summary is not None
