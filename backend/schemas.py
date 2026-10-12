"""
Pydantic v2 schemas for API requests, responses, and WebSocket payloads.
Enforces strict validation, size bounds, syntax verification, and error envelopes.
"""

import ast
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class StandardErrorResponse(BaseModel):
    error: str
    detail: Any
    trace_id: str
    timestamp: str


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    source_type: str = Field("snippet", pattern=r"^(snippet|zip|demo|folder)$")

    @field_validator("name")
    @classmethod
    def validate_safe_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Project name cannot be empty or whitespace.")
        # Reject dangerous path traversal sequences
        if ".." in clean or clean.startswith(("/", "\\")):
            raise ValueError("Project name contains invalid path traversal sequences.")
        # Reject illegal Windows/POSIX filename characters
        if re.search(r'[<>:"/\\|?*]', clean):
            raise ValueError('Project name contains illegal characters: <>:"/\\|?*')
        return clean


class ProjectCreate(ProjectBase):
    code_snippet: Optional[str] = Field(None, max_length=250000)

    @field_validator("code_snippet")
    @classmethod
    def validate_python_syntax(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        clean = v.strip()
        if not clean:
            raise ValueError("Code snippet cannot be empty or pure whitespace.")
        # Perform AST syntax parsing check
        try:
            ast.parse(v)
        except SyntaxError as e:
            raise ValueError(f"Python syntax error at line {e.lineno or 1}, column {e.offset or 1}: {e.msg}")
        return v


class ProjectResponse(ProjectBase):
    id: str
    source_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BugResponse(BaseModel):
    id: str
    run_id: str
    file_path: str
    line_number: int
    title: str
    description: str
    beginner_explanation: Optional[str] = None
    severity: str
    category: str
    confidence: float
    causal_chain: Optional[str] = None
    proposed_fix_diff: Optional[str] = None
    fix_verified: bool
    verification_output: Optional[str] = None
    consensus_score: float
    deduplication_key: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FileRiskResponse(BaseModel):
    id: str
    run_id: str
    file_path: str
    loc: int
    cyclomatic_complexity: float
    security_smells: int
    risk_score: float
    risk_level: str
    details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TestResultResponse(BaseModel):
    id: str
    run_id: str
    test_name: str
    test_file: str
    target_function: Optional[str] = None
    status: str
    duration_ms: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    is_flaky: bool
    flake_rerun_count: int

    model_config = ConfigDict(from_attributes=True)


class MutationRecordResponse(BaseModel):
    id: str
    run_id: str
    file_path: str
    line_number: int
    mutation_type: str
    original_op: Optional[str] = None
    mutated_op: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class AgentLogResponse(BaseModel):
    id: str
    run_id: str
    seq: Optional[int] = None
    agent_name: str
    timestamp: datetime
    level: str
    message: str
    metadata_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DebateMessageResponse(BaseModel):
    id: str
    run_id: str
    round_num: int
    agent_from: str
    agent_to: str
    issue_ref: Optional[str] = None
    claim: str
    rebuttal: Optional[str] = None
    resolution: Optional[str] = None
    agreement_score: float

    model_config = ConfigDict(from_attributes=True)


class RunResponse(BaseModel):
    id: str
    project_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_files: int
    lines_of_code: int
    risk_score: float
    code_coverage: float
    mutation_score: float
    suite_health_score: float
    bugs_count: int
    fixes_verified_count: int
    current_agent: str
    progress_pct: int
    executive_summary: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedRunsResponse(BaseModel):
    items: List[RunResponse]
    total: int
    limit: int
    offset: int


class RunDetailResponse(RunResponse):
    error_message: Optional[str] = None
    technical_report: Optional[str] = None
    bugs: List[BugResponse] = []
    file_risks: List[FileRiskResponse] = []
    test_results: List[TestResultResponse] = []
    mutation_records: List[MutationRecordResponse] = []
    debates: List[DebateMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class StartRunRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    llm_provider: Optional[str] = Field("offline", pattern=r"^(offline|gemini|openai|ollama|google|gpt)$")
    idempotency_key: Optional[str] = Field(None, max_length=255)


class ActionResponse(BaseModel):
    success: bool
    message: str
    run_id: Optional[str] = None


class MetricsResponse(BaseModel):
    uptime_seconds: float
    total_requests: int
    active_runs: int
    completed_runs: int
    failed_runs: int
    interrupted_runs: int
    avg_latency_ms: float
    database_status: str
