# SentinelMesh Baseline Test Report

## 1. System Environment & Tooling
- **OS**: Windows 11 Enterprise (win32)
- **Python**: 3.13.14 (Virtual Environment `.venv`)
- **Pytest**: 9.1.1 (with pytest-asyncio 1.4.1, pytest-cov 7.1.0)
- **Node.js**: v24.18.0
- **npm**: 11.16.0
- **Vite**: 8.3.4
- **React**: 19.2.8
- **Tailwind CSS**: 4.3.3

## 2. Test Execution Baseline
### Backend Pytest Suite
- **Command**: `.venv\Scripts\python -m pytest`
- **Result**: `37 passed, 1 warning in 15.82s`
- **Warnings**:
  - `StarletteDeprecationWarning: Using 'httpx' with 'starlette.testclient' is deprecated; install 'httpx2' instead.` (harmless library warning).

### Frontend Vite Production Build
- **Command**: `npm run build --prefix frontend`
- **Result**: `✓ built in 619ms` (0 errors)
- **Assets**:
  - `dist/index.html` (1.20 kB)
  - `dist/assets/index-pv0h3tNk.css` (42.17 kB)
  - `dist/assets/index-BpWZ8uy9.js` (403.28 kB)

### Linter (Oxlint)
- **Command**: `npm run lint --prefix frontend`
- **Result**: `0 errors, 48 warnings` (unused imports cleaned).

## 3. Dev Server Blank Screen Root Cause & Remediation
- **Symptom**: When opening `http://localhost:5173/`, the screen was blank white.
- **Root Cause**: `useEffect` was used on line 47 of `frontend/src/components/assistant/MeshAssistant.jsx` to forward prompts, but only `useState` was imported from `'react'`. React encountered `ReferenceError: useEffect is not defined` during mount, unmounting the entire tree.
- **Remediation**:
  1. Updated import in `MeshAssistant.jsx` to `import React, { useState, useEffect } from 'react';`.
  2. Implemented top-level `ErrorBoundary` in `frontend/src/main.jsx` to gracefully catch and display runtime errors without blanking the viewport.
  3. Verified both dev (`npm run dev` on port 5173) and production (`uvicorn` serving `dist/` on port 8000) render successfully.

## 4. Fullstack Verification & Acceptance Results (Phases 1–5)

### Automated Test Matrix
| Category | Check | Expected | Actual | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | Pytest Suite (`tests/`) | 42 passed, 0 failures | 42 passed, 0 failures in 19.96s | **PASS** |
| **Backend** | Guardrail G1 Tag & Branch | `pre-fullstack-fix` & `backup-pre-fullstack-fix` | Verified in git tree | **PASS** |
| **Backend** | Backward Compatibility (G2) | All 17 existing REST/WS endpoints preserved | Verified intact in `test_api.py` and `test_persistence.py` | **PASS** |
| **Backend** | V2 Endpoints (`test_api_v2.py`) | Workflow, Impact, Compare, Webhook, Trends | 5/5 passing in `test_api_v2.py` | **PASS** |
| **Frontend** | Vite Build (`dist/`) | 0 build errors | ✓ built in 566ms | **PASS** |
| **Frontend** | Code Linting (Oxlint) | 0 errors | 0 errors detected | **PASS** |
| **Frontend** | Chatbot Grounding (D5) | 10/10 questions answered or honest fallback | 10/10 passed with citation chips | **PASS** |
| **Data Flow** | E2E Swarm Flow (D3) | Demo launch → 9 agents complete | Run `#b41c1c1f` completed, health score calculated | **PASS** |
| **Honesty** | Grounded Metrics (D4) | Zero fabricated numbers; real formulas cited | All metrics grounded in real telemetry | **PASS** |
| **A11y** | WCAG 2.1 AA (D6) | Focus rings, AAA/AA color contrast, no traps | All 25 components compliant | **PASS** |
| **Visual** | Responsive Screenshots (D7) | 18 full-page screenshots (1440px & 768px) | 18/18 verified in `docs/screenshots/` | **PASS** |

### Summary of Fullstack Bugs Remediated
1. **Frontend Blank Screen Crash**:
   - *Cause*: `ReferenceError: useEffect is not defined` in `MeshAssistant.jsx`.
   - *Fix*: Added `useEffect` import and added top-level `ErrorBoundary` in `main.jsx`.
2. **Missing Export in Lucide React**:
   - *Cause*: `Github` icon is not exported by `lucide-react` in Rolldown Vite build.
   - *Fix*: Replaced with inline `GitRepoIcon` SVG.
3. **Pipeline "Reproduce: 0 confirmed" Discrepancy**:
   - *Cause*: Status stored as uppercase `"FAILED"` in backend, while frontend compared `t.status === "failed"`.
   - *Fix*: Normalized status comparison `String(t.status).toLowerCase() === "failed"` and consumed real `failed_tests_count` column.
4. **Hardcoded Banner & KPI Subtext**:
   - *Cause*: Hardcoded sentences ("Both fixes pass... One critical item... is still open" and "1 high · 2 medium") copied from initial mockups.
   - *Fix*: Dynamically generated from real `bugs` severities and verification states.
5. **FastAPI Route Parameter Interception on `/api/runs/compare`**:
   - *Cause*: Parameterized path `@app.get("/api/runs/{run_id}")` was registered before literal `@app.get("/api/runs/compare")`, matching `run_id="compare"` and returning 404.
   - *Fix*: Positioned `/api/runs/compare` before the parameterized route.
6. **SQLite Dynamic Migration**:
   - *Cause*: SQLite requires dynamic `ALTER TABLE` execution in `auto_migrate()` when adding columns to existing databases.
   - *Fix*: Added dynamic column checks and additions in `backend/database.py:auto_migrate()`.
