# SentinelMesh: API & UI Control Inventory

Comprehensive mapping of all backend endpoints, WebSocket interfaces, and interactive UI controls.

---

## 1. FastAPI REST & WebSocket Endpoints Inventory

| Method | Path | Request Schema | Response Schema | Expected Status Codes | Description |
|---|---|---|---|---|---|
| `GET` | `/api/health` | None | `HealthResponse` | `200` | Liveness, readiness & database connectivity check |
| `GET` | `/api/metrics` | None | `MetricsResponse` | `200` | System telemetry, throughput, latency, queue & active runs |
| `POST` | `/api/projects` | `ProjectCreate` | `ProjectResponse` | `201`, `400`, `422` | Create project from code snippet or local folder |
| `POST` | `/api/projects/upload` | Form-data (`name`: str, `file`: zip) | `ProjectResponse` | `201`, `400`, `413`, `422` | Secure zip upload with zip-slip & zip-bomb protection |
| `GET` | `/api/projects` | Query (`limit`: int, `offset`: int) | `List[ProjectResponse]` | `200` | Paginated list of registered projects |
| `GET` | `/api/projects/{project_id}` | Path param (`project_id`: UUID) | `ProjectResponse` | `200`, `404` | Get single project metadata |
| `POST` | `/api/demo/launch` | Query (`llm_provider`: str) | `LaunchDemoResponse` | `201`, `409` | Clones demo ecommerce microservice & starts run |
| `POST` | `/api/runs` | `StartRunRequest` | `StartRunResponse` | `201`, `404`, `409`, `422` | Create & start a swarm analysis run (idempotent) |
| `GET` | `/api/runs` | Query (`project_id`: str, `limit`: int, `offset`: int) | `PaginatedRunsResponse` | `200` | List runs with pagination and status filters |
| `GET` | `/api/runs/{run_id}` | Path param (`run_id`: UUID) | `RunDetailResponse` | `200`, `404` | Full run details (bugs, risks, tests, debates) |
| `POST` | `/api/runs/{run_id}/cancel` | Path param (`run_id`: UUID) | `ActionResponse` | `200`, `404`, `400` | Cancels active run and terminates sandbox processes |
| `POST` | `/api/runs/{run_id}/retry` | Path param (`run_id`: UUID) | `StartRunResponse` | `201`, `404`, `409` | Retries or resumes an interrupted/failed run |
| `GET` | `/api/runs/{run_id}/logs` | Path param (`run_id`: UUID), Query (`since_seq`: int) | `List[AgentLogResponse]` | `200`, `404` | Event-sourced sequence log entries for replay |
| `GET` | `/api/runs/{run_id}/patch` | Path param (`run_id`: UUID) | `text/plain` | `200`, `404` | Unified git-compatible diff patch file |
| `GET` | `/api/runs/{run_id}/report` | Path param (`run_id`: UUID), Query (`format`: md/html/json) | `JSON` or `text/html` or `text/plain` | `200`, `404`, `400` | Executive and technical audit report export |
| `GET` | `/api/backup` | None | `application/octet-stream` (SQLite WAL dump) | `200`, `500` | Database backup export archive |
| `WS` | `/ws/runs/{run_id}` | WebSocket protocol | Stream of JSON event frames | `101`, `404` | Real-time bidirectional telemetry & log stream |

---

## 2. Interactive UI Controls to API Mapping

| UI Component | Control / Action | User Interaction | Triggered API Call | Payload / Parameters |
|---|---|---|---|---|
| **Header** | "Run Demo Project" | Click button | `POST /api/demo/launch` | `?llm_provider={selectedProvider}` |
| **Header** | "Analyze Code" | Click button | Opens `NewProjectModal` | None (Client-side modal state) |
| **Header** | "LLM Engine" dropdown | Change selection | Updates React state | Passed in future run creations |
| **Header** | "Export PR Patch" | Click button | `GET /api/runs/{id}/patch` | Browser download trigger |
| **Header** | "Report (HTML)" | Click button | `GET /api/runs/{id}/report` | `?format=html` in new tab |
| **Hero Banner** | "Launch Demo Project" | Click button | `POST /api/demo/launch` | `?llm_provider={selectedProvider}` |
| **Hero Banner** | "Upload Code Repository" | Click button | Opens `NewProjectModal` | None |
| **NewProjectModal** | "Paste Code Snippet" Tab | Submit form | 1. `POST /api/projects`<br>2. `POST /api/runs` | 1. `{"name": name, "code_snippet": code, "source_type": "snippet"}`<br>2. `{"project_id": id, "llm_provider": provider}` |
| **NewProjectModal** | "Upload Project (.zip)" Tab | Submit form | 1. `POST /api/projects/upload`<br>2. `POST /api/runs` | 1. Multipart form (`name`, `file`)<br>2. `{"project_id": id, "llm_provider": provider}` |
| **NewProjectModal** | "Load Pre-Seeded Demo" | Click button | `POST /api/demo/launch` | `?llm_provider={selectedProvider}` |
| **KPICards** | Metric Cards | Display / View | `GET /api/runs/{id}` | Telemetry from active run |
| **AgentNetworkGraph** | 9 Agent Nodes | Click agent node | Inspect node details | Displays role and live state |
| **LiveTerminal** | Log Level Filter | Change dropdown | Client-side filter | Filters displayed logs by level |
| **LiveTerminal** | Copy Logs button | Click button | Client-side clipboard | Copies lines to system clipboard |
| **LiveTerminal** | Auto-Scroll button | Click toggle | Client-side ref scroll | Toggles automatic scrolling |
| **RiskHeatmap** | Code Module Tiles | Click file tile | Client-side drawer | Shows LOC, Complexity, Smells |
| **BugExplorer** | Severity Filter | Change dropdown | Client-side filter | Filters bug table rows |
| **BugExplorer** | Category Filter | Change dropdown | Client-side filter | Filters bug table rows |
| **BugExplorer** | Bug Table Row | Click row | Opens side drawer | Displays Causal Trace & Diff |
| **BugExplorer Drawer** | "Explain Like I'm a Beginner" | Click switch toggle | Swaps display mode | Switches between trace and ELI5 |
| **BugExplorer Drawer** | "Copy Diff" button | Click button | Client-side clipboard | Copies unified diff to clipboard |
| **AgentDebatePanel** | Debate Rounds Ledger | Display / View | `GET /api/runs/{id}` & WS | Displays Critic audit debates |

---

## 3. Global Error Contract

Every endpoint adheres to a standardized JSON error envelope:
```json
{
  "error": "ErrorCategoryIdentifier",
  "detail": "Human-readable explanation of failure",
  "trace_id": "c8f94e87-5dc2-4a59-977e-32401670ee4c",
  "timestamp": "2026-10-12T09:15:00.000Z"
}
```
No endpoint returns raw string errors or generic HTML pages.
