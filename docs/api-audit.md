# SentinelMesh API & Route Audit

**Audit Date:** 2026-10-29  
**Target:** Live Backend (`http://localhost:8000`) & Offline Engine  
**Contract Invariant:** Zero backend modifications. Front-end adapts strictly to existing response shapes.

---

## 1. REST Endpoints Inventory

### System & Telemetry
| Method | Route | Description | Request Payload | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Service liveness & SQLite WAL ping | None | `{ status: string, platform: string, version: string, database: { connected: bool, latency_ms: float }, timestamp: string }` |
| `GET` | `/api/metrics` | Server metrics & run counters | None | `{ uptime_seconds: float, total_requests: int, active_runs: int, completed_runs: int, failed_runs: int, interrupted_runs: int, avg_latency_ms: float, database_status: string }` |
| `GET` | `/api/backup` | Binary SQLite database snapshot | None | Binary SQLite stream (`application/octet-stream`) |

### Projects
| Method | Route | Description | Request Payload | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/projects` | List all registered projects | None | `List[ProjectResponse]` (`[{ id, name, description, source_type, source_path, created_at, updated_at }]`) |
| `GET` | `/api/projects/{id}` | Retrieve single project | None | `ProjectResponse` |
| `POST` | `/api/projects` | Register project from code snippet | `{ name: string, code_snippet: string, source_type: "snippet" }` | `ProjectResponse` |
| `POST` | `/api/projects/upload` | Upload `.zip` repository | `multipart/form-data` (`file`, query `name`) | `ProjectResponse` |

### Runs & Agent Swarm
| Method | Route | Description | Request Payload | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/demo/launch` | 1-Click pre-seeded e-commerce demo | Query `llm_provider` (`"offline"\|"gemini"\|"openai"`) | `{ message: string, run_id: string, project_id: string }` |
| `POST` | `/api/runs` | Launch analysis run on project | `{ project_id: string, llm_provider: string, idempotency_key?: string }` | `{ message: string, run_id: string }` |
| `GET` | `/api/runs` | Paginated list of historical runs | Query `limit=int`, `offset=int` | `{ items: List[RunResponse], total: int, limit: int, offset: int }` |
| `GET` | `/api/runs/{id}` | Comprehensive run details | None | `RunDetailResponse` (details below) |
| `POST` | `/api/runs/{id}/cancel` | Abort in-flight run | None | `{ success: bool, message: string, run_id: string }` |
| `POST` | `/api/runs/{id}/retry` | Resume / retry interrupted run | None | `{ success: bool, message: string, run_id: string }` |
| `GET` | `/api/runs/{id}/logs` | Event-sourced log replay | Query `since_seq=int` | `List[AgentLogResponse]` (`[{ id, run_id, seq, agent_name, timestamp, level, message, metadata_json }]`) |
| `GET` | `/api/runs/{id}/patch` | Download unified fix patch | None | Text stream (`text/x-diff` or attachment) |
| `GET` | `/api/runs/{id}/report` | Technical audit report | Query `format="html"\|"json"` | HTML document or JSON object |

---

## 2. WebSocket Real-Time Stream

### Route: `ws://localhost:8000/ws/runs/{run_id}`
Bidirectional live telemetry stream providing instant updates during agent swarm execution.

| Event Type (`event_type`) | Payload Contents (`data`) | Description |
| :--- | :--- | :--- |
| `log` | `{ message, agent_name, level, timestamp, data }` | Monospaced log lines emitted by individual agents |
| `agent_state` | `{ state: "RUNNING"\|"COMPLETED"\|"FAILED"\|"THINKING"\|"IDLE", details: string }` | Transition of specific agent node in the swarm |
| `telemetry` | `{ current_agent, key, value, progress_pct, ... }` | Live progress updates & intermediate scores |
| `debate` | `{ round_num, agent_from, agent_to, claim, rebuttal, resolution, agreement_score, issue_ref }` | Critic vs. Auto-Fix consensus debate rounds |
| `run_status` | `{ status: "running"\|"completed"\|"failed"\|"interrupted" }` | Overall pipeline lifecycle status |

---

## 3. Data Shapes Analysis (`RunDetailResponse`)

The root object returned by `GET /api/runs/{id}` contains:
- `id`: Unique run identifier (e.g. `run_9a8f...`)
- `project_id`: Associated project ID
- `status`: `"pending"` | `"running"` | `"completed"` | `"failed"` | `"interrupted"`
- `started_at`, `completed_at`: ISO timestamp strings
- `total_files`: Integer count of audited files
- `lines_of_code`: Total LOC analyzed
- `risk_score`: Overall composite risk percentage (0–100)
- `code_coverage`: Percentage of lines covered by generated tests (0–100)
- `mutation_score`: Percentage of AST mutants killed (0–100)
- `suite_health_score`: Composite suite reliability score (0–100)
- `bugs_count`: Total defects identified
- `fixes_verified_count`: Total self-healing fixes successfully verified in the sandbox
- `current_agent`: Currently executing agent (`orchestrator`, `static_analysis_agent`, etc.)
- `progress_pct`: Percentage of pipeline completion (0–100)
- `bugs`: Array of `BugResponse`
  - `id`: Bug identifier
  - `file_path`: Relative file path (e.g. `order_processor.py`)
  - `line_number`: 1-based defect line number
  - `title`: Short descriptive title
  - `description`: Detailed diagnostic
  - `beginner_explanation`: Plain-language explanation (if generated)
  - `severity`: `"CRITICAL"` | `"HIGH"` | `"MEDIUM"` | `"LOW"`
  - `category`: `"LOGIC"` | `"SECURITY"` | `"INPUT_VALIDATION"` | `"CONCURRENCY"`
  - `confidence`: Confidence float (0.0 – 1.0)
  - `causal_chain`: JSON-serialized list of causal trace steps
  - `proposed_fix_diff`: Unified diff text
  - `fix_verified`: Boolean indicating if sandbox re-run passed
  - `verification_output`: Output log from sandbox pytest run
  - `consensus_score`: Swarm agreement score (0–100)
- `file_risks`: Array of `FileRiskResponse`
  - `file_path`: Path of monitored file
  - `loc`: Lines of code
  - `cyclomatic_complexity`: Complexity score
  - `security_smells`: Smell count
  - `risk_score`: Calculated risk percentage
  - `risk_level`: `"CRITICAL"` | `"HIGH"` | `"MEDIUM"` | `"LOW"`
- `test_results`: Array of `TestResultResponse`
  - `test_name`: Name of generated/executed test
  - `test_file`: Test file location
  - `status`: `"passed"` | `"failed"`
  - `duration_ms`: Execution time in milliseconds
  - `error_message`: Assertion error / exception message
  - `stack_trace`: Formatted Python traceback
- `debates`: Array of `DebateMessageResponse`
  - `round_num`: Deliberation round index
  - `agent_from`: Proposing agent
  - `agent_to`: Challenging agent (e.g. `critic_agent`)
  - `claim`: Proposed defect or fix claim
  - `rebuttal`: Critic audit objection
  - `resolution`: Certified resolution
  - `agreement_score`: Consensus score (0.0 – 1.0)
  - `issue_ref`: Bug ID or target reference

---

## 4. UI Derivations & Adapter Mapping (`src/api/adapters.js`)

To satisfy the product-grade information architecture without changing the backend:
1. **Self-Healing Pipeline Stages**:
   - `Detect`: Derived from `bugs_count`
   - `Reproduce`: Derived from `test_results.filter(t => t.status === "failed").length` or `bugs_count`
   - `Propose fix`: Derived from `bugs.filter(b => b.proposed_fix_diff).length`
   - `Verify`: Derived from `fixes_verified_count` of `bugs_count`
   - `Open PR`: Status is "Waiting" if unmerged, "Ready" when verified fixes exist
2. **Merge Readiness Checklist**:
   - Derived directly from `bug.fix_verified`, `bug.verification_output`, `runData.test_results`, and `runData.mutation_score`.
3. **Bug Workflow States**:
   - `Open` -> `Fix proposed` -> `Verified` -> `PR opened` -> `Merged` -> `Dismissed`.
   - Initial state computed from `bug.proposed_fix_diff` and `bug.fix_verified`. User actions ("Dismiss", "Open PR", "Mark Merged") are persisted client-side via `localStorage` per `run_id:bug_id`.
4. **Mesh Assistant Chatbot**:
   - Queries loaded `RunDetailResponse` directly in-memory, extracting exact grounded matches, test failures, and debate records. Cites real sources (`file:line`, `debate #round`, `test name`) with zero hallucinations.
