# SentinelMesh Implementation Plan & Task List

SentinelMesh is an Intelligent Multi-Agent Software Testing and Bug Analysis Platform featuring 9 cooperating AI agents, an AST/mutation testing engine, sandboxed execution, self-healing bug fix verification, and a modern "mission-control" real-time dashboard.

---

## Architecture Overview
```
                     +---------------------------------------+
                     |         SentinelMesh UI               |
                     |  (React + Vite + Framer + Tailwind)   |
                     +-------------------+-------------------+
                                         | REST & WebSocket
                     +-------------------v-------------------+
                     |         FastAPI Backend               |
                     |  (Async Event Bus, Run Lifecycle)     |
                     +-------------------+-------------------+
                                         |
     +-----------------------------------v-----------------------------------+
     |                     SentinelMesh Orchestrator                         |
     |            (Coordinates 9 Parallel & Sequential Agents)               |
     +---+---------+---------+---------+---------+---------+---------+---+---+
         |         |         |         |         |         |         |   |
         |         |         |         |         |         |         |   +--> Report Agent
         |         |         |         |         |         |         +------> Critic Agent
         |         |         |         |         |         +----------------> Auto-Fix Agent
         |         |         |         |         +--------------------------> Root Cause Agent
         |         |         |         +------------------------------------> Bug Classifier
         |         |         +----------------------------------------------> Test Execution Agent
         |         +--------------------------------------------------------> Test Generation Agent
         +------------------------------------------------------------------> Static Analysis Agent
                                         |
                     +-------------------v-------------------+
                     |      Subprocess Sandbox Isolation     |
                     |  (AST Mutator, Coverage, Pytest)      |
                     +---------------------------------------+
```

---

## Milestones & Phased Execution

### Phase 1: Foundation & Backend Architecture
- [ ] Workspace structure: `backend/`, `agents/`, `sandbox/`, `frontend/`, `tests/`, `docs/`, `demo/`
- [ ] Database schema (SQLite + SQLAlchemy models):
  - Projects, Runs, FileNodes, Bugs, TestSuites, MutationScores, AgentLogs, DebateLogs
- [ ] Lightweight LLM Layer:
  - Abstract `LLMProvider` interface
  - Providers: Offline Rule/Heuristic Engine (100% offline, zero-key demo ready), Google Gemini, OpenAI, Ollama local
- [ ] Asynchronous Event Bus & Streaming Message Protocol:
  - Agent state transitions: `IDLE` -> `THINKING` -> `RUNNING` -> `COMPLETED` / `FAILED`
  - Real-time terminal log stream, progress percentage, agent-to-agent message bus

### Phase 2: Agent Architecture (9 Cooperating Agents)
- [ ] 1. **Orchestrator Agent**: Controls pipeline flow, manages dependency graph of tasks, handles retries and self-healing loop.
- [ ] 2. **Static Analysis Agent**: Python AST analysis, radon cyclomatic complexity, bandit security audits, code smells, dead code, file-level Risk Score formula.
- [ ] 3. **Test Generation Agent**: Produces pytest unit tests, edge-case checks, boundary value tests, and property-based test suites.
- [ ] 4. **Test Execution Agent**: Runs tests in sandbox, gathers coverage percentages, runs flaky-test detection loop (rerun N times with jitter).
- [ ] 5. **Bug Classification Agent**: Identifies failed tests & static vulnerabilities; categorizes severity (Critical/High/Medium/Low), category (logic, security, performance, concurrency, validation), deduplication.
- [ ] 6. **Root Cause Agent**: Traces stack traces back to AST line numbers, builds step-by-step causal chains.
- [ ] 7. **Auto-Fix Agent**: Generates unified diffs (`patch`), applies them in isolated test workspace, re-executes tests to verify if bug is fixed -> marks as `Verified Fix`.
- [ ] 8. **Critic/Reviewer Agent**: Challenges bug findings, flags false positives, triggers debate rounds, assigns consensus score (0-100%).
- [ ] 9. **Report Agent**: Synthesizes executive summary, risk posture, test health, exports to JSON/Markdown/HTML.

### Phase 3: Isolated Sandbox & Mutation Testing Engine
- [ ] Subprocess execution manager with strict timeouts, process limits, virtualenv isolation, and environment cleaning.
- [ ] Custom AST-based Mutation Testing Engine:
  - Mutates comparison operators (`==` to `!=`, `<` to `<=`, etc.)
  - Mutates arithmetic operators (`+` to `-`, `*` to `/`, etc.)
  - Mutates boolean constants & return statements
  - Executes test suite against each mutant and calculates mutation kill score: Killed / Total * 100%.

### Phase 4: FastAPI REST API & WebSocket Streaming Server
- [ ] `/api/projects`: upload zip, paste snippet, import demo project
- [ ] `/api/runs`: create, trigger, cancel, get status, list history
- [ ] `/api/runs/{id}/bugs`: get bugs, root cause, verified fixes, PR patch export
- [ ] `/api/runs/{id}/reports`: export full report (HTML, JSON, Markdown)
- [ ] `/api/demo`: launch pre-configured demo project instantly
- [ ] `/ws/runs/{id}`: WebSocket endpoint pushing live telemetry, node updates, log messages, and debates

### Phase 5: Mission-Control React Dashboard
- [ ] Modern dark aesthetic: glassmorphism, glowing status rings, cyberpunk/orbital accents
- [ ] Live Agent Network Graph: visual topology of the 9 agents with pulsing active states, connecting data pulses, and execution timers
- [ ] Real-time Terminal Log Console: streaming logs with timestamp and severity color
- [ ] Metric Telemetry Cards: Bugs Found, Code Coverage %, Mutation Kill Score %, Suite Health Score (0-100)
- [ ] Codebase Risk Heatmap: interactive file tree/treemap with risk density indicators
- [ ] Bug Explorer with drawer:
  - Code inspection & highlighted bug line
  - Unified diff viewer for auto-fixes with "Verified Fix" status tag
  - Root Cause Causal Chain diagram
  - "Explain Like I'm a Beginner" toggle
  - Export PR Patch button
- [ ] Agent Debate Panel: logs of Critic challenges and final consensus scores
- [ ] Pre-seeded Demo Trigger button for 1-click evaluation

### Phase 6: Pre-Seeded Buggy Demo & Unit Testing
- [ ] Realistic multi-file project in `/demo` (`PaymentEngine`, `UserValidator`, `OrderProcessor`, `InventoryService`) with subtle real-world bugs (off-by-one, race condition, float division zero error, SQL injection string concat, unhandled NoneType).
- [ ] High-coverage automated test suite for the platform itself in `/tests`.

### Phase 7: Verification & Packaging
- [ ] Run backend and agent test suite to ensure green passing status (>80% coverage).
- [ ] Build & run frontend, run live demo end-to-end.
- [ ] Verify using browser subagent with video recording artifact.
- [ ] Add `run.bat`, `run.sh`, `requirements.txt`, `README.md`, and `docs/architecture.md`.
