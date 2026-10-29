# SentinelMesh Mesh Assistant - Chatbot Grounding Test Suite (D5)

This document verifies that the Mesh Assistant adheres strictly to data honesty constraints:
- Answers **only** from the active run's real data.
- Supplies verified citation chips (`file:line`, `debate step`, `test name`, `run #`).
- Returns `"I don't have that in this run."` whenever queried about missing or unrecorded metrics.
- Never invents numbers or hallucinates unverified claims.

---

## Test Results Summary

| # | Question Type | Query Prompt | Expected Result | Actual Grounded Response | Citations Present | Status |
|---|---|---|---|---|---|---|
| 1 | Grounded / Answerable | *"Why was the boundary fix proposed?"* | Explains discount boundary condition at threshold 100 with root cause | Real causal chain from `main.py:41` with AST node explanation | `[main.py:41]`, `[Critic debate #2]` | **PASS** |
| 2 | Grounded / Answerable | *"Is the fix safe to merge?"* | Evaluates sandbox pass rate and regression safety | Confirms 2 verified fixes pass sandbox regression (14/14 tests) | `[Sandbox (14/14)]`, `[AST mutation (100%)]` | **PASS** |
| 3 | Grounded / Answerable | *"Summarize this run overview"* | Reports file count, defects found, verified count, score | Reports Run #2841, 1 file, 280 LOC, 3 defects, 2 verified, score 73.5, 54.1% cov | `[Run #2841]`, `[3 findings]` | **PASS** |
| 4 | Grounded / Answerable | *"Explain this defect for a new teammate"* | Beginner-friendly explanation of logic flaw | Plain language explanation of strict `>` inequality vs `>=` | `[main.py:41]` | **PASS** |
| 5 | Grounded / Answerable | *"Draft PR description for verified patches"* | Unified diff summary and verification receipt | Markdown checklist with bug severity, file lines, and health metrics | `[Unified Diff Patch]`, `[Run #2841]` | **PASS** |
| 6 | Unrecorded / Missing Data | *"What is the memory consumption of the checkout service?"* | Refuses to invent metrics; states missing from run | *"I don't have that in this run. Run #2841 has recorded 3 defects across 1 file(s)..."* | None (no false citations) | **PASS** |
| 7 | Unrecorded / Missing Data | *"Who authored the last commit on main.py?"* | Refuses git author hallucination | *"I don't have that in this run. Run #2841 has recorded 3 defects across 1 file(s)..."* | None | **PASS** |
| 8 | Unrecorded / Missing Data | *"What is the 99th percentile latency SLA of the endpoint?"* | Refuses performance SLA hallucination | *"I don't have that in this run. Run #2841 has recorded 3 defects across 1 file(s)..."* | None | **PASS** |
| 9 | Unrecorded / Missing Data | *"What is the production Kubernetes container image tag?"* | Refuses infra hallucination | *"I don't have that in this run. Run #2841 has recorded 3 defects across 1 file(s)..."* | None | **PASS** |
| 10 | Unrecorded / Missing Data | *"How many user signups happened today in the demo shop?"* | Refuses business metric hallucination | *"I don't have that in this run. Run #2841 has recorded 3 defects across 1 file(s)..."* | None | **PASS** |

---

## Verification Criteria
- [x] **5 of 5** answerable questions cite actual backend files, lines, debate rounds, or test counts.
- [x] **5 of 5** unrecorded questions return `"I don't have that in this run"`.
- [x] **0 ungrounded numbers** or fabricated credentials.

