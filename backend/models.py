"""
SQLAlchemy ORM models for SentinelMesh.
Tracks projects, runs, bugs, test suites, mutation testing, agent logs, and debate logs.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from backend.database import Base


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(String(50), default="snippet")  # "snippet", "zip", "demo", "folder"
    source_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    runs = relationship("Run", back_populates="project", cascade="all, delete-orphan", order_by="desc(Run.started_at)")


class Run(Base):
    __tablename__ = "runs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    idempotency_key = Column(String(255), unique=True, nullable=True)
    trace_id = Column(String(64), nullable=True)
    status = Column(String(50), default="pending")  # pending, running, completed, failed, cancelled, interrupted
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Core Metrics
    total_files = Column(Integer, default=0)
    lines_of_code = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)             # 0 to 100
    code_coverage = Column(Float, default=0.0)          # 0 to 100
    mutation_score = Column(Float, default=0.0)         # 0 to 100
    suite_health_score = Column(Float, default=0.0)     # 0 to 100
    bugs_count = Column(Integer, default=0)
    fixes_verified_count = Column(Integer, default=0)
    failed_tests_count = Column(Integer, default=0)
    agent_durations = Column(Text, nullable=True)  # JSON mapping: agent_name -> seconds
    token_cost_usd = Column(Float, default=0.0)

    # Progress & State
    current_agent = Column(String(100), default="orchestrator")
    progress_pct = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    executive_summary = Column(Text, nullable=True)
    technical_report = Column(Text, nullable=True)

    project = relationship("Project", back_populates="runs")
    bugs = relationship("Bug", back_populates="run", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="run", cascade="all, delete-orphan")
    mutation_records = relationship("MutationRecord", back_populates="run", cascade="all, delete-orphan")
    file_risks = relationship("FileRisk", back_populates="run", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="run", cascade="all, delete-orphan", order_by="AgentLog.seq")
    debates = relationship("DebateMessage", back_populates="run", cascade="all, delete-orphan", order_by="DebateMessage.round_num")

    __table_args__ = (
        Index("idx_runs_project_status", "project_id", "status"),
        Index("idx_runs_started_at", "started_at"),
    )


class Bug(Base):
    __tablename__ = "bugs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    run_id = Column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(512), nullable=False)
    line_number = Column(Integer, default=1)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    beginner_explanation = Column(Text, nullable=True)

    # Classification
    severity = Column(String(50), default="MEDIUM")      # CRITICAL, HIGH, MEDIUM, LOW
    category = Column(String(50), default="LOGIC")       # LOGIC, SECURITY, PERFORMANCE, CONCURRENCY, INPUT_VALIDATION
    confidence = Column(Float, default=0.85)             # 0.0 to 1.0

    # Root Cause & Fix
    causal_chain = Column(Text, nullable=True)           # JSON array of causal trace steps
    proposed_fix_diff = Column(Text, nullable=True)      # Unified diff patch
    fix_verified = Column(Boolean, default=False)        # Self-healing badge
    verification_output = Column(Text, nullable=True)
    consensus_score = Column(Float, default=0.90)        # Critic agent score
    deduplication_key = Column(String(255), nullable=True)

    # Workflow & Merge-Gate Telemetry
    workflow_state = Column(String(50), default="open")  # open, fix_proposed, verified, pr_opened, merged, dismissed
    dismiss_reason = Column(String(255), nullable=True)
    assignee = Column(String(100), nullable=True)
    tests_passed_after_fix = Column(Integer, nullable=True)
    tests_failed_after_fix = Column(Integer, nullable=True)
    regression_count = Column(Integer, default=0)
    critic_verdict = Column(String(50), default="NOT_REVIEWED")  # PASSED, FAILED, NOT_REVIEWED
    callers_count = Column(Integer, default=0)
    affected_callers = Column(Text, nullable=True)  # JSON array of caller names

    run = relationship("Run", back_populates="bugs")

    __table_args__ = (
        Index("idx_bug_run_severity", "run_id", "severity"),
        Index("idx_bug_dedup", "run_id", "deduplication_key"),
    )


class FileRisk(Base):
    __tablename__ = "file_risks"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    run_id = Column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(512), nullable=False)
    loc = Column(Integer, default=0)
    cyclomatic_complexity = Column(Float, default=1.0)
    security_smells = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)             # 0 - 100
    risk_level = Column(String(50), default="LOW")      # LOW, MEDIUM, HIGH, CRITICAL
    details = Column(Text, nullable=True)               # JSON details

    run = relationship("Run", back_populates="file_risks")

    __table_args__ = (
        Index("idx_file_risks_run", "run_id", "risk_score"),
    )


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    run_id = Column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    test_name = Column(String(255), nullable=False)
    test_file = Column(String(512), nullable=False)
    target_function = Column(String(255), nullable=True)
    status = Column(String(50), default="PASSED")       # PASSED, FAILED, SKIPPED, FLAKY
    duration_ms = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    is_flaky = Column(Boolean, default=False)
    flake_rerun_count = Column(Integer, default=0)

    run = relationship("Run", back_populates="test_results")

    __table_args__ = (
        Index("idx_test_results_run_status", "run_id", "status"),
    )


class MutationRecord(Base):
    __tablename__ = "mutation_records"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    run_id = Column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(512), nullable=False)
    line_number = Column(Integer, default=1)
    mutation_type = Column(String(100), nullable=False) # OP_REPLACE, CONST_FLIP, BOUNDARY_OFF, RETURN_MUTATE
    original_op = Column(String(100), nullable=True)
    mutated_op = Column(String(100), nullable=True)
    status = Column(String(50), default="KILLED")       # KILLED, SURVIVED, TIMED_OUT

    run = relationship("Run", back_populates="mutation_records")

    __table_args__ = (
        Index("idx_mutation_records_run", "run_id", "status"),
    )


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    run_id = Column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    seq = Column(Integer, primary_key=False, nullable=True)  # Event-sourced sequence number
    agent_name = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=utcnow)
    level = Column(String(20), default="INFO")          # INFO, WARN, ERROR, AGENT_STATE, TELEMETRY
    message = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)

    run = relationship("Run", back_populates="agent_logs")

    __table_args__ = (
        Index("idx_agent_logs_run_seq", "run_id", "seq"),
        Index("idx_agent_logs_run_ts", "run_id", "timestamp"),
    )


class DebateMessage(Base):
    __tablename__ = "debate_messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    run_id = Column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    round_num = Column(Integer, default=1)
    agent_from = Column(String(100), nullable=False)
    agent_to = Column(String(100), nullable=False)
    issue_ref = Column(String(255), nullable=True)
    claim = Column(Text, nullable=False)
    rebuttal = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    agreement_score = Column(Float, default=1.0)        # 0.0 to 1.0

    run = relationship("Run", back_populates="debates")

    __table_args__ = (
        Index("idx_debates_run", "run_id", "round_num"),
    )
