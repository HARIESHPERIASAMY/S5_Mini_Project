# SentinelMesh UI v2 — 3-Minute Demo Walkthrough Script

This script guides evaluators and stakeholders through the optimal 3-minute end-to-end demo of **SentinelMesh**, demonstrating autonomous test synthesis, multi-agent debate, sandboxed self-healing, and grounded verification.

---

## Prerequisites & Launch (0:00 - 0:20)
1. **Start the Platform**:
   - Backend & Offline Engine:
     ```bash
     .venv\Scripts\python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
     ```
   - Frontend Dashboard (Development mode):
     ```bash
     npm run dev --prefix frontend
     ```
2. **Open Dashboard**:
   - Navigate to `http://localhost:5173/` in your browser.
   - Notice the **Start Screen**: Clean project setup cards (Run Demo Project, Upload ZIP, Paste Snippet), LLM engine selection (Offline zero-key engine by default), and architecture summary.

---

## Step 1: Launch Pre-Seeded FinTech Demo (0:20 - 0:50)
1. On the Start Screen, click **"Run Demo Project"**.
2. SentinelMesh automatically clones the pre-seeded buggy FinTech microservice (`ecommerce` service featuring boundary comparison, division-by-zero, SQL injection hazards).
3. **Observation**:
   - The UI transitions into the **Live Run** view.
   - The top banner displays the real-time Swarm execution status (`Swarm Active: @static_analysis_agent`, `@test_generation_agent`, etc.).
   - The 9-stage pipeline reflects active agent states with live timestamps and progress indicators.
   - Toggle **"Raw logs"** to inspect streamed structured telemetry and agent logs filtered by severity.

---

## Step 2: Overview & Grounded Metrics (0:50 - 1:30)
1. Once the swarm pipeline finishes (progress 100%), switch to **Overview** via the left sidebar.
2. **Observation**:
   - **Verdict Banner**: Real health score (e.g. `36.2` or `73.5`), dynamic defect summary (`X defects flagged, Y fixes already verified`), and grounded banner text.
   - Click **"Why [Score]? See breakdown"**: Drawer slides open displaying the exact formula from `agents/test_execution_agent.py:136`:
     $$\text{Health Score} = \min\left(100, (\text{Pass Rate} \times 0.5) + (\text{Coverage} \times 0.5) - \text{Flaky Penalty}\right)$$
   - **KPI Cards**: Real defect count, real severity breakdown (`1 high · 1 critical`), verified fixes, and mutation score.
   - **Self-Healing Pipeline**: 5 stages (Detect → Reproduce → Propose fix → Verify → Open PR) with confirmed reproduced defects.

---

## Step 3: Deep Defect Triage & Self-Healing Verification (1:30 - 2:15)
1. Click **Findings** in the sidebar (or click **"Review top fix"** in the overview banner).
2. The split-pane interface shows the **File Tree** on the left and the **Findings Table** with severity badges.
3. Select the first defect (e.g., `Strict inequality boundary` at `main.py:41`).
4. The **Defect Detail Drawer** slides in with 4 focused tabs:
   - **Fix Tab**: Clear "What Failed" explanation, before-and-after unified syntax diff, and "What-If" impact simulation.
   - **Proof Tab**:
     - 5 discrete **Merge Readiness** checks: Sandbox test pass, zero regressions, mutation resistance, call graph impact, and critic agent approval.
     - **Proof of Fix Receipt**: Includes deterministic **Patch hash (SHA-256)** and exact sandbox completion timestamp.
   - **Debate Tab**: Multi-agent consensus debate dialogue between Bug Classifier and Critic agents.
   - **Ask Tab**: Pre-populated contextual prompts for instant AI clarification.
5. Change the workflow state to **"Verified"** or click **"Open PR"**:
   - The change is persisted immediately to the SQLite database via `PATCH /api/runs/{id}/bugs/{bug_id}/workflow`.

---

## Step 4: Grounded Mesh Assistant & Run History (2:15 - 3:00)
1. Click the floating **"Ask Mesh Assistant"** button in the lower right.
2. Ask a factual question grounded in this run:
   - *"Why was the boundary fix proposed?"* → Assistant cites `main.py:41` with clickable citation chips.
   - *"Is the fix safe to merge?"* → Assistant checks real sandbox pass rates and flags any open defects.
3. Ask an unknown question not present in this run:
   - *"What is the memory consumption of the checkout service?"* → Assistant answers honestly: *"I don't have that in this run. Run #[id] has recorded X defects across 1 file(s)..."*, with zero fabricated numbers.
4. Navigate to **Run History**:
   - View past executed runs recorded in SQLite.
   - Click **"Compare runs"** to view side-by-side score delta, coverage delta, and categorized bug diffs (Fixed / New / Unchanged).
5. Open the **Export** menu in the TopBar:
   - Download **OASIS SARIF 2.1.0**, **JUnit XML**, **PR Patch (.patch)**, or **Patch Bundle Archive (.zip)**.

---
*Demo complete! SentinelMesh proves autonomous software testing, real self-healing verification, and complete data honesty.*

