# SentinelMesh Features Requiring Future Backend Enhancements

The current frontend implementation is 100% functional against the live FastAPI / SQLite offline backend (`http://localhost:8000`). For advanced enterprise extensions, the following items are currently adapted or mock-flagged:

---

## 1. Interactive "What-If" Sandbox Re-Execution
- **Current Adapter Behavior**: In the Mesh Assistant, queries that ask "What if threshold changes to X" provide analytical answers derived from the static AST analysis and the causal chain. If `USE_MOCKS=true`, an experimental preview response is presented clearly labelled as simulated.
- **Backend Enhancement Needed**: An endpoint `POST /api/sandbox/re-execute` that accepts temporary parameter overrides and executes targeted pytest runs in an ephemeral container without creating a full project run.

---

## 2. Server-Side Bug State Transitions & Assignments
- **Current Adapter Behavior**: Bug lifecycle states (`Open` -> `Fix proposed` -> `Verified` -> `PR opened` -> `Merged`, plus `Dismissed` and `Assignee`) are persisted in browser `localStorage` keyed by `sentinel_workflow_{run_id}_{bug_id}`.
- **Backend Enhancement Needed**: Endpoints `PATCH /api/runs/{run_id}/bugs/{bug_id}/status` and `PATCH /api/runs/{run_id}/bugs/{bug_id}/assignee` to persist collaborative triage decisions in the SQLite database across multi-user sessions.

---

## 3. Webhook Delivery (Slack & Email Alerts)
- **Current Adapter Behavior**: The Integrations and Settings views allow configuring webhook URLs and notification preferences, storing them locally. A test alert indicates that notification dispatch is stored locally.
- **Backend Enhancement Needed**: Background webhook dispatcher in `backend/main.py` that posts JSON payloads to configured endpoints upon run completion.

---

## 4. Automated Git Push / Direct GitHub PR Creation
- **Current Adapter Behavior**: Clicking "Open PR" downloads the verified `.patch` file and opens the GitHub PR action helper modal with ready-to-paste git commands and PR descriptions.
- **Backend Enhancement Needed**: Integration with GitHub OAuth / Personal Access Tokens to automate `git checkout -b fix-branch`, `git apply patch`, and `gh pr create` directly on remote git repositories.
