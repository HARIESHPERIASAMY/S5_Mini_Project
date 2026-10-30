# SentinelMesh System Map (Architecture & Data Flow)

## 1. Backend REST & WebSocket Endpoints

| Method | Endpoint | Description | Called By Frontend? | Call Location / View |
|---|---|---|---|---|
| `GET` | `/api/health` | Service health status check | Yes (automated checks) | Health check ping |
| `GET` | `/api/metrics` | Swarm telemetry & throughput metrics | No *(Uncalled)* | - |
| `POST` | `/api/projects` | Create snippet/repo project record | Yes | `StartScreen.jsx`, `NewProjectModal.jsx` |
| `POST` | `/api/projects/upload` | Upload `.zip` repository archive | Yes | `StartScreen.jsx`, `NewProjectModal.jsx` |
| `GET` | `/api/projects` | List projects | No *(Uncalled)* | - |
| `GET` | `/api/projects/{project_id}` | Get project by ID | No *(Uncalled)* | - |
| `POST` | `/api/demo/launch` | Autonomous demo launch (`demo-shop`) | Yes | `StartScreen.jsx`, `NewProjectModal.jsx` |
| `POST` | `/api/runs` | Launch new analysis run for project | Yes | `StartScreen.jsx`, `NewProjectModal.jsx` |
| `GET` | `/api/runs` | Paginated run history (`limit`, `offset`) | Yes | `RunHistoryView.jsx`, `App.jsx` |
| `GET` | `/api/runs/{run_id}` | Detailed run metrics, bugs, debates | Yes | `App.jsx`, `CompareRunsModal.jsx` |
| `POST` | `/api/runs/{run_id}/cancel` | Interrupt active swarm run | No *(Uncalled)* | - |
| `POST` | `/api/runs/{run_id}/retry` | Re-run swarm with fresh seed | No *(Uncalled)* | - |
| `GET` | `/api/runs/{run_id}/logs` | Paginated agent execution logs | No *(Uncalled)* | WebSocket used instead |
| `GET` | `/api/runs/{run_id}/patch` | Unified diff patch (`.patch`) | Yes | `TopBar.jsx`, `ReportsView.jsx`, `DefectDetailDrawer.jsx` |
| `GET` | `/api/runs/{run_id}/report` | Standalone HTML technical audit | Yes | `TopBar.jsx`, `ReportsView.jsx` |
| `GET` | `/api/backup` | SQLite streaming database backup | No *(Uncalled)* | - |
| `WS` | `/ws/runs/{run_id}` | Event-sourced telemetry WebSocket | Yes | `App.jsx` (Live Terminal & Run state) |

---

## 2. The 9 Swarm Agents

1. **`OrchestratorAgent` (`agents/orchestrator_agent.py`)**:
   - Manages the Directed Acyclic Graph (DAG) state machine across all 9 agents.
   - Dispatches workspace setup, coordinates inputs/outputs, handles interruption.
2. **`StaticAnalysisAgent` (`agents/static_analysis_agent.py`)**:
   - Parses Python AST for cyclomatic complexity, security code smells, division without zero check, unbound variables.
   - Populates `file_risks` and baseline AST nodes.
3. **`TestGenerationAgent` (`agents/test_generation_agent.py`)**:
   - Generates property-based and boundary edge tests focusing on input limits and condition inequalities.
4. **`TestExecutionAgent` (`agents/test_execution_agent.py`)**:
   - Runs tests in isolated sandbox runner.
   - Computes code coverage and calculates the **Suite Health Score** using the exact formula:
     $$\text{health\_score} = \operatorname{round}\big(\max(0.0, \min(100.0, (\text{pass\_rate} \times 0.5) + (\text{cov\_pct} \times 0.5) - \text{flaky\_penalty})), 1\big)$$
     *(Source: `agents/test_execution_agent.py:136-140`)*
5. **`BugClassificationAgent` (`agents/bug_classification_agent.py`)**:
   - Categorizes bugs (`LOGIC`, `SECURITY`, `CRITICAL`, `BOUNDARY`), assigns severity and confidence.
6. **`RootCauseAgent` (`agents/root_cause_agent.py`)**:
   - Computes causal chains from stack traces and AST path traversals.
7. **`AutoFixAgent` (`agents/auto_fix_agent.py`)**:
   - Synthesizes unified diff patches targeting minimal surface area repairs.
8. **`CriticAgent` (`agents/critic_agent.py`)**:
   - Evaluates patches via multi-agent debate and re-executes tests in the sandbox to verify the fix.
9. **`ReportAgent` (`agents/report_agent.py`)**:
   - Generates HTML reports, unified patches, and exports audit receipts.

---

## 3. Database Schema & Models

- **`Project` (`projects` table)**:
  `id`, `name`, `source_type` (`demo` / `snippet` / `upload`), `file_path`, `code_snippet`, `created_at`.
- **`Run` (`runs` table)**:
  `id`, `project_id`, `status` (`pending`, `running`, `completed`, `failed`), `progress_pct`, `current_agent`, `suite_health_score`, `code_coverage`, `mutation_score`, `total_files`, `lines_of_code`, `fixes_verified_count`, `bugs_count`, `created_at`, `completed_at`.
- **`Bug` (`bugs` table)**:
  `id`, `run_id`, `title`, `description`, `category`, `severity`, `file_path`, `line_number`, `confidence`, `proposed_fix_diff`, `fix_verified`, `consensus_score`, `beginner_explanation`, `created_at`.
- **`FileRisk` (`file_risks` table)**:
  `id`, `run_id`, `file_path`, `risk_score`, `bugs_count`, `complexity`.
- **`TestResult` (`test_results` table)**:
  `id`, `run_id`, `test_name`, `status`, `duration_ms`, `error_message`, `is_regression`.
- **`MutationRecord` (`mutation_records` table)**:
  `id`, `run_id`, `mutant_id`, `operator`, `file_path`, `line_number`, `killed`, `killing_test`.
- **`AgentLog` (`agent_logs` table)**:
  `id`, `run_id`, `agent_name`, `level`, `message`, `timestamp`.
- **`DebateMessage` (`debate_messages` table)**:
  `id`, `run_id`, `round_number`, `agent_name`, `stance`, `argument`, `confidence`, `timestamp`.

---

## 4. Frontend View Data Flow

| Frontend View | Consumed Routes | Adapter Derivations |
|---|---|---|
| **Start Screen** | `POST /api/demo/launch`, `POST /api/projects`, `POST /api/projects/upload`, `POST /api/runs` | Language detection from snippet |
| **Overview** | `GET /api/runs/{id}`, `GET /api/runs?limit=25` | Health breakdown, Self-healing pipeline strip, Findings preview |
| **Live Run** | `GET /api/runs/{id}`, `WS /ws/runs/{id}` | Agent pipeline status, Plain language activity timeline, Telemetry logs |
| **Findings** | `GET /api/runs/{id}`, `GET /api/runs/{id}/patch` | File tree risk badges, Master-detail table, 3-state Merge Gate, What-If simulation |
| **Agents** | `GET /api/runs/{id}`, `WS /ws/runs/{id}` | Active agent network graph, Agent debate consensus replay |
| **Run History** | `GET /api/runs?limit=25`, `GET /api/runs/{id}` | Sparkline trend (shown when $\ge 2$ runs), Cross-run comparison modal |
| **Reports** | `GET /api/runs/{id}/patch`, `GET /api/runs/{id}/report` | OASIS SARIF 2.1.0 generator, JUnit XML generator, Patch ZIP bundle |
| **Integrations** | `GET /api/runs/{id}` | GitHub Actions pipeline YAML generator, PR certification comment template |
| **Settings** | `GET /api/runs/{id}` | Swarm parameters, 9-agent matrix, Offline Zero-Key token cost calculator |
| **Mesh Assistant** | `GET /api/runs/{id}` | Grounded Q&A against active run telemetry with citation chips |

---

## 5. Discrepancies & Missing Integrations (Targeted for Phase 2 & 3)

1. **Bug Workflow Persistence**: The frontend updates bug status in `localStorage`, but the backend lacks a persistent `workflow_state` column on `bugs` and a `PATCH /api/runs/{run_id}/bugs/{bug_id}/workflow` endpoint.
2. **Impact Simulation**: The frontend estimates impact mathematically ($+3.6\text{ pts}$); a dedicated backend endpoint `POST /api/runs/{run_id}/simulate-impact` will provide authoritative simulation.
3. **Merge Gate Telemetry**: `after_fix_test_results`, `regression_count`, and `callers_count` are partially inferred by the Verifier; backend will expose them directly on `Bug` and `Run`.
4. **Run Comparison**: Backend endpoint `GET /api/runs/compare?base_id=...&target_id=...` will provide server-side matching of Fixed / New / Unchanged defects.
5. **Data Consistency**: Bug counts and reproduced counts must strictly align (`failed_tests` count vs `bugs` count).

