# SentinelMesh UI v2 Upgrade Plan

## Overview & Architecture
SentinelMesh is an autonomous multi-agent software testing and self-healing bug analysis platform.
- **Frontend Stack**: React 19, Vite 8, Tailwind CSS v4 (`@tailwindcss/vite`), Lucide React icons, Framer Motion.
- **Serving Architecture**:
  - In development: Vite dev server on `http://localhost:5173`.
  - In production / runtime: FastAPI backend mounts `frontend/dist` at `http://localhost:8000/`. Launch scripts (`run.ps1`, `run.bat`, `run.sh`) run `uvicorn backend.main:app` which serves both the REST/WebSocket API and the built front-end assets directly.
  - Build command: `npm run build` (produces optimized output in `frontend/dist`).

---

## 1. Inventory of Data Sources

### A. API Endpoints Used by the UI
1. `POST /api/demo/launch?llm_provider={provider}`: Initiates pre-seeded e-commerce demo analysis run. Returns `{ message, run_id, project_id }`.
2. `POST /api/projects`: Registers new project snippet. Request body: `{ name, code_snippet, source_type }`. Returns `ProjectResponse`.
3. `POST /api/projects/upload?name={name}`: Uploads project zip archive (multipart/form-data). Returns `ProjectResponse`.
4. `POST /api/runs`: Launches analysis run on created project. Request body: `{ project_id, llm_provider }`. Returns `{ message, run_id }`.
5. `GET /api/runs/{run_id}`: Polled during and after runs for comprehensive telemetry, bugs, test results, file risks, and debates. Returns `RunDetailResponse`.
6. `GET /api/runs/{run_id}/patch`: Downloads unified fix patch text.
7. `GET /api/runs/{run_id}/report?format=html`: Downloads standalone HTML technical audit report.
8. `GET /api/health`: Health and latency check (`{ status, database, latency_ms }`).
9. `ws://localhost:8000/ws/runs/{run_id}`: Live real-time bidirectional WebSocket telemetry stream.

### B. WebSocket Stream Events & Payload Shapes
- `log`: `{ event_type: "log", agent_name: string, level: "INFO"|"WARN"|"ERROR"|"TELEMETRY", timestamp: ISOString, data: { message: string, ... } }`
- `agent_state`: `{ event_type: "agent_state", agent_name: string, data: { state: "RUNNING"|"COMPLETED"|"FAILED"|"THINKING"|"IDLE", details: string }, timestamp: ISOString }`
- `telemetry`: `{ event_type: "telemetry", data: { current_agent: string, key: string, value: any, ... } }`
- `debate`: `{ event_type: "debate", data: DebateMessageResponse }`
- `run_status`: `{ event_type: "run_status", data: { status: "running"|"completed"|"failed"|"interrupted" } }`

### C. Complete JSON Fields Consumed by the UI
1. **Run Details (`RunDetailResponse`)**:
   - `id`: string
   - `status`: string (`"pending"` | `"running"` | `"completed"` | `"failed"` | `"interrupted"`)
   - `started_at`, `completed_at`: datetime ISO strings
   - `total_files`: integer
   - `lines_of_code`: integer
   - `risk_score`: float (0 - 100)
   - `code_coverage`: float (0 - 100)
   - `mutation_score`: float (0 - 100)
   - `suite_health_score`: float (0 - 100)
   - `bugs_count`: integer
   - `fixes_verified_count`: integer
   - `current_agent`: string
   - `progress_pct`: integer (0 - 100)
   - `executive_summary`: string (optional)
   - `bugs`: Array of `BugResponse`
   - `file_risks`: Array of `FileRiskResponse`
   - `test_results`: Array of `TestResultResponse`
   - `mutation_records`: Array of `MutationRecordResponse`
   - `debates`: Array of `DebateMessageResponse`
2. **Bug Details (`BugResponse`)**:
   - `id`: string
   - `file_path`: string
   - `line_number`: integer
   - `title`: string
   - `description`: string
   - `beginner_explanation`: string (optional)
   - `severity`: `"CRITICAL"` | `"HIGH"` | `"MEDIUM"` | `"LOW"`
   - `category`: `"LOGIC"` | `"SECURITY"` | `"INPUT_VALIDATION"` | `"CONCURRENCY"` | string
   - `confidence`: float (0.0 - 1.0)
   - `causal_chain`: string (JSON serialized string array or raw text)
   - `proposed_fix_diff`: string (Unified diff with `---`, `+++`, `@@`, `-`, `+`)
   - `fix_verified`: boolean
   - `verification_output`: string (Sandbox pytest / mutant verification result)
   - `consensus_score`: float (0 - 100)
3. **File Risk (`FileRiskResponse`)**:
   - `file_path`: string
   - `loc`: integer
   - `cyclomatic_complexity`: float
   - `security_smells`: integer
   - `risk_score`: float (0 - 100)
   - `risk_level`: `"CRITICAL"` | `"HIGH"` | `"MEDIUM"` | `"LOW"`
4. **Test Result (`TestResultResponse`)**:
   - `test_name`: string
   - `test_file`: string
   - `target_function`: string
   - `status`: `"passed"` | `"failed"`
   - `duration_ms`: float
   - `error_message`: string
   - `stack_trace`: string
5. **Debate Message (`DebateMessageResponse`)**:
   - `round_num`: integer
   - `agent_from`: string
   - `agent_to`: string
   - `claim`: string
   - `rebuttal`: string
   - `resolution`: string
   - `agreement_score`: float (0.0 - 1.0)
   - `issue_ref`: string (optional)

---

## 2. Element IDs, Data Attributes & JS Functions Preserved
- **DOM / Mounting**:
  - `id="root"`: React mount point in `index.html`.
- **Core Handler Functions & Hooks**:
  - `handleLaunchDemo`: One-click launch of the demo project.
  - `handleSubmitSnippet`: Submission of custom Python snippets.
  - `handleUploadZip`: Submission of repository zip packages.
  - `handleExportPatch`: Download of PR-ready unified diff patch.
  - `handleDownloadReport`: Download of HTML audit report.
  - `handleCopyDiff`: Clipboard copy of fix diff.
  - `handleCopyLogs`: Clipboard copy of formatted telemetry stream.
  - `getSeverityBadge`, `getRiskColor`, `getStatusColor`, `getLevelStyle`: Helper formatters.

---

## 3. Design System Specification (Light, Calm, Professional)
- **Palette**:
  - Page Background: `#F4F6FA` with subtle dotted SVG mesh background
  - Surface Cards: `#FFFFFF`
  - Border: `#E3E8F0`
  - Text Main: `#0F172A`
  - Text Muted: `#5B6577`
  - Accent Primary: `#2563EB`
  - Success: `#16A34A`
  - Danger / Critical: `#DC2626`
  - Warning / High: `#D97706`
  - AI / Critic: `#7C3AED`
- **Soft Badge Tints**:
  - Red / Critical: Background `#FEECEC`, Text `#B42318`
  - Green / Verified: Background `#E7F8EE`, Text `#14753B`
  - Amber / Warning: Background `#FFF4E0`, Text `#9A5B00`
  - Blue / Info: Background `#EAF1FF`, Text `#1D4ED8`
  - Violet / AI Critic: Background `#F1EAFE`, Text `#6D28D9`
- **Typography**:
  - Headings: `Manrope`, system-ui, -apple-system, sans-serif
  - Body: `Inter`, system-ui, -apple-system, sans-serif
  - Code & Logs: `JetBrains Mono`, Consolas, monospace
  - Full system font offline fallbacks included.
- **Component Geometry**:
  - Cards: White surface, 1px border (`#E3E8F0`), 16px radius, soft shadow (`0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.03)`).
  - Buttons & Inputs: 10px radius, >= 40px height, clear keyboard focus ring (`ring-2 ring-blue-500 ring-offset-2`).
  - Color only carries meaning and is always paired with clear text labels.

---

## 4. Mapping of UI Sections (A through I) to Data Sources

### A. Sticky Top Bar
- **Elements**: Logo icon, "SentinelMesh" title, tagline "Autonomous Software Testing & Self-Healing Bug Analysis Platform".
- **Model Chip**: Select dropdown bound to `llmProvider` (`"offline"`, `"gemini"`, `"openai"`), connection dot reflecting live WebSocket state (Green = connected, Amber = reconnecting/offline).
- **Actions**:
  1. "Run Demo Project" (Primary blue button, triggers `handleLaunchDemo`)
  2. "Analyze Code" (Triggers `onOpenNewProject` modal)
  3. "Report (PR Patch)" (Triggers `handleExportPatch`, active when verified fixes exist)
  4. "Report (HTML)" (Triggers `handleDownloadReport`)

### B. Readiness Strip
- **Headline**: Computed dynamically from backend run data:
  `"{bugs_count} defect(s) flagged, and {fixes_verified_count} fix(es) already verified"` (or `"System ready for analysis"` if no active run).
- **Suite Health Ring**: Circular SVG meter showing `suite_health_score` (0-100) with color mapping (>=75 green, 50-74 amber, <50 red).
- **5-Item Release Gate**:
  - Threshold constants block at top of module:
    ```javascript
    export const RELEASE_GATE_THRESHOLDS = {
      MIN_COVERAGE: 80,      // %
      MIN_MUTATION: 60,      // %
      MIN_SUITE_HEALTH: 75,  // /100
      MAX_OPEN_CRITICAL: 0,  // count
      ALL_FIXES_VERIFIED: true
    };
    ```
  - Gate 1: "All Defects Have Verified Fixes" (`fixes_verified_count >= bugs_count` when bugs > 0).
  - Gate 2: "Test Coverage >= 80%" (`code_coverage >= 80`).
  - Gate 3: "Mutation Score >= 60%" (`mutation_score >= 60`).
  - Gate 4: "Zero Open Critical Defects" (`critical_bugs_open === 0`).
  - Gate 5: "Suite Health >= 75" (`suite_health_score >= 75`).
- **Quick Action Buttons**:
  - "Review the fix": Selects top defect (`bugs[0]`) and smoothly scrolls to Defect Explainer.
  - "Explain the bug": Toggles beginner/plain-language explanation mode on the selected defect.

### C. KPI Row (5 Cards)
- Card 1: **Bugs Found**: `bugs_count` + Code Risk % (`risk_score`).
- Card 2: **Verified Fixes**: `fixes_verified_count` + `% Self-Healed` (`Math.round(fixes_verified / bugs_count * 100)`).
- Card 3: **Test Coverage**: `code_coverage`% + progress bar.
- Card 4: **Mutation Score**: `mutation_score`% + "Mutants Killed".
- Card 5: **Suite Health**: `suite_health_score` / 100 + Resilient / Flaky badge.

### D. Two Columns (Swarm & Telemetry)
- **Left (~60%): Live Agent Swarm**:
  - Switchable view: **Network Graph** vs. **Flight Path** (horizontal sequential pipeline).
  - Network Graph: 9 cooperating agent nodes restyled in light theme with clear status badges (`RUNNING`, `COMPLETED`, `IDLE`, `FAILED`).
  - Flight Path View: Step-by-step horizontal pipeline with connecting progress lines.
  - Report Agent Status Bar: Sits below the graph/pipeline indicating current swarm phase.
- **Right (~40%): Telemetry and Agent Log**:
  - Light console theme (white background, crisp dark text, syntax highlighting).
  - Colored tag per agent with soft badge tint.
  - Agent filter dropdown (filter by specific agent name).
  - Level filter dropdown (`ALL`, `INFO`, `WARN`, `ERROR`, `TELEMETRY`).
  - "Pause scroll" toggle button.
  - "Copy log" button.

### E. Coverage Risk Heatmap
- One tile per module from `runData.file_risks`, sorted descending by `risk_score`.
- Displays: file path, risk score, LOC, Cyclomatic Complexity, Security Smells.
- Legend: Critical (>=70%), High (>=45%), Medium (>=25%), Low (<25%).
- Interactive filtering: Clicking a file tile sets `filterFile`, automatically filtering the Bug Classification Ledger below to that file.

### F. Bug Classification and Self-Healing Ledger (Full Width)
- Columns: Location (`file_path:line_number`), Severity badge, Category chip, Defect Title, Self-Healing Fix badge.
- Interactive controls:
  - Severity dropdown filter (`ALL`, `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
  - Category dropdown filter (`ALL`, `LOGIC`, `SECURITY`, `INPUT_VALIDATION`, `CONCURRENCY`).
  - Search input box (filters rows across file path, title, category, and description).
- Row interaction: Clicking a row selects that bug, highlights the row with soft blue tint and accent border, and loads it into the Defect Explainer directly underneath.

### G. Defect Explainer (Full Width, Under Ledger)
- **Header**:
  - Severity badge (`CRITICAL`, `HIGH`, etc.)
  - Location badge (`file_path:line_number`)
  - Defect Title
  - Verified Fix badge (`fix_verified`)
  - Confidence percentage (`Math.round(confidence * 100)%`)
  - Tabs: **Explain** | **Evidence** | **Debate**
- **Tab 1: Explain**:
  - **Summary Strip (3 Boxes)**:
    - `THE MISTAKE`: High-level summary of the bug mechanism (derived from AST flaw / defect title / description).
    - `THE IMPACT`: Real-world consequence if unpatched (derived from failure diagnostic / test exception).
    - `THE FIX`: The concrete remedy applied (derived from resolution / diff summary).
  - **Left Column**:
    1. *Where the defect is*: Code excerpt around `line_number` extracted from unified diff context, with line numbers. The defect line has a red left border, light red background `#FEECEC`, and a "Defect line" tag. Risky token is highlighted with carets `^^^^` and label.
    2. *What goes wrong*: Input condition that triggers the flaw, 3 numbered steps from cause to failure (parsed from `causal_chain`), real error or traceback text in a code box (from `test_results` or description), failing test name chip, category chip.
  - **Right Column**:
    3. *Correct code*: Fixed code snippet from `proposed_fix_diff` with added/changed lines highlighted in soft green (`#E7F8EE`) with line numbers and safe line indicator.
    4. *Why this works*: 2-3 tick-marked bullet points explaining how the fix resolves the edge case.
    5. *Verification Box*: Green verification card showing "Critic approved, N of N tests pass" plus sandbox execution details from `verification_output`.
    6. *Actions*: "Copy corrected code", "Download patch" (client-side blob download as `.patch` file), "Open PR patch" (triggers existing endpoint).
- **Tab 2: Evidence**:
  - Displays failing test details from `test_results` matching the file: test name, duration, assertion error message, and formatted stack trace.
  - If no explicit test result exists for this bug, gracefully shows bug description diagnostics without fake data.
- **Tab 3: Debate**:
  - Displays Critic and Swarm debate rounds relevant to this bug (filtered from `runData.debates`). Shows agent claim, Critic rebuttal, resolution, and agreement score.
- **Data Rule Handling**: All fields come strictly from backend data. Any missing block is hidden gracefully. If generic wording is needed for mistaked/impact summaries, it is explicitly labelled "General guidance".

### H. Critic Agent and Multi-Agent Debate
- Full-width collapsible section.
- Styled as a clean multi-agent message thread with agent avatars/tags, message bubbles, agreement score, claim, rebuttal, and resolution.

### I. Slim Sticky Status Bar
- Fixed at the bottom of the viewport:
  - Backend connection status indicator (Online / Offline / Reconnecting).
  - Active Run ID (truncated with copy option).
  - Last updated timestamp.
  - Quick health ping / latency display.

---

## 5. Responsive Behavior & Accessibility
- **Desktop (1440px+)**: Two-column layout (60/40) for Swarm and Telemetry; full-width ledger and explainer.
- **Tablet (1024px)**: Swarm and Telemetry stack vertically into single columns.
- **Mobile (768px)**: Ledger switches to mobile card view; Defect Explainer stacks into a single vertical column.
- **Accessibility**: Keyboard navigable (Tab, Shift+Tab, Enter on rows), ARIA roles and labels, text contrast > 4.5:1.

---

## 6. Exact Files Planned to Edit
1. `frontend/index.html`: Set light theme class, typography font preloads/links, page metadata.
2. `frontend/src/index.css`: Light theme design system CSS variables, typography definitions, dotted background pattern, clean scrollbar and card utility styles.
3. `frontend/src/App.jsx`: State orchestration for flight path view, file filter from heatmap, selected bug passing to Defect Explainer, status bar, and connection-lost banner.
4. `frontend/src/components/Header.jsx`: Light theme styling, sticky navigation, model selector chip, primary actions.
5. `frontend/src/components/ReadinessStrip.jsx` (*New component*): Release gate calculation, circular health ring, threshold constants, quick action buttons.
6. `frontend/src/components/KPICards.jsx`: Light theme 5-card row with soft shadows, subtle badges, and trend indicators.
7. `frontend/src/components/AgentNetworkGraph.jsx`: Light theme topology SVG + Network / Flight path toggle + Report agent status bar.
8. `frontend/src/components/LiveTerminal.jsx`: Light theme console, agent filter, level filter, pause scroll, copy logs.
9. `frontend/src/components/RiskHeatmap.jsx`: Light theme tiles, risk-sorting, interactive file selection that filters the bug ledger.
10. `frontend/src/components/BugExplorer.jsx`: Search box, table ledger, selection highlight, full integration with Defect Explainer.
11. `frontend/src/components/DefectExplainer.jsx` (*New component*): Dedicated full-width explainer directly under ledger with Explain / Evidence / Debate tabs, 3-box summary strip, code carets, correct code diff, and patch actions.
12. `frontend/src/components/AgentDebatePanel.jsx`: Light theme collapsible message thread.
13. `frontend/src/components/StatusBar.jsx` (*New component*): Slim sticky footer showing connection state, run ID, and last update time.
14. `frontend/src/components/NewProjectModal.jsx`: Light theme modal for snippet/zip submission.

---

## 7. Verification Plan (Step 5)
1. Verify against `S5 Mini Project_BACKUP_original`: compare live demo run output between original and v2 to ensure identical numbers, logs, bugs, fixes, and debates.
2. Verify all buttons, dropdowns, filters, search box, toggles, copy actions, and download actions.
3. Run `python -m pytest` to prove backend test suite passes 37/37 with zero regressions.
4. Compare file hashes against `backend_files_hashes_baseline.csv` to confirm zero backend files were touched.
5. Run `npm run build --prefix frontend` to ensure production Vite bundle builds with zero errors.
6. Test responsive layouts at 1440px, 1024px, and 768px.
7. Write `README_UI_V2.md` and `VERIFICATION.md` detailing rollback instructions.

