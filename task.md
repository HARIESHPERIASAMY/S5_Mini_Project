# SentinelMesh Backend Hardening & API Audit Pass Task Checklist

## Phase 1: Inventory & Audit
- [x] Complete REST & WebSocket endpoint inventory (`docs/api-inventory.md`)
- [x] Map all interactive UI controls to endpoints (`docs/api-inventory.md`)
- [x] Create comprehensive smoke-testing harness (`scripts/audit.py`)
- [x] Execute audit and record real metrics (`docs/audit-report.md`) - **100.0% PASS**

## Phase 2: Correctness & Error Handling
- [x] Global JSON exception handlers returning `{"error", "detail", "trace_id", "timestamp"}` (no plain-text / HTML)
- [x] Strict Pydantic v2 validation (safe project names, AST syntax check on snippets, size limits)
- [x] Consistent response envelopes and HTTP status codes (201 Created for POSTs, 405 Method Not Allowed, 422 for bad AST)
- [x] Windows & Linux safety (pathlib, UTF-8, proper child process handling)
- [x] Idempotency keys to prevent duplicate runs
- [x] Cancellation endpoint `/api/runs/{id}/cancel` leaving no orphan processes
- [x] Fix Analyze Code pasted snippet bug and frontend response parsing in `frontend/src/App.jsx`
- [x] 15/15 unit tests passing

## Phase 3: Persistence & Recovery
- [x] SQLite WAL mode, `busy_timeout = 5000`, `foreign_keys = ON` in `backend/database.py`
- [x] Dynamic auto-migration for SQLite schema evolution
- [x] Event-sourced run logs with sequential `seq` IDs and `since_seq` WebSocket replay
- [x] Crash recovery: detect runs left in `running` state on startup, mark `interrupted`, enable resume/retry
- [x] Paginated run history (`GET /api/runs?page=1&page_size=20`)
- [x] Database backup endpoint (`GET /api/backup`)
- [ ] Integration verification tests for persistence & crash recovery

## Phase 4: Performance & Benchmarking
- [ ] Create `scripts/benchmark.py` measuring real p50/p95/p99 latency
- [ ] Measure end-to-end demo execution time (target: <15s)
- [ ] Benchmark generated 50-file (target: <60s) and 100-file projects
- [ ] Verify memory stability across consecutive runs
- [ ] Output real benchmarks to `docs/performance-report.md`

## Phase 5: Sandbox & Security
- [ ] Verify subprocess sandbox limits, timeouts, and process tree termination (`psutil`)
- [ ] Verify upload safety: zip-slip, zip-bomb ratio checks, file size caps
- [ ] Resilience: agent timeout and graceful fallback to offline heuristic engine
- [ ] Produce `docs/resilience-report.md`

## Phase 6: Observability
- [x] `/api/health` with database ping latency
- [x] `/api/metrics` with request counts, active runs, and latency tracking
- [x] Structured logs with distributed `trace_id`

## Phase 7: Comprehensive Test Suite & Proof
- [ ] Comprehensive pytest suite for all endpoints and failure modes
- [ ] Fault-injection tests (crash recovery, corrupt zip, mid-run cancel, WebSocket reconnect)
- [ ] Concurrency test (simultaneous runs)
- [ ] Soak test (sequential runs, memory stability)
- [ ] Measure test coverage targeting 85%+
- [ ] Final verification and summary
