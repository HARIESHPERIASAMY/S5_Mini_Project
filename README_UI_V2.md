# SentinelMesh UI v2 Overview

## Summary of Changes
SentinelMesh has been upgraded to a modern, calm, high-contrast, light-themed engineering interface (**UI v2**) designed for autonomous software testing, risk analysis, and self-healing verification.

All updates are strictly front-end:
- **Zero backend changes**: All 25 backend files in `backend/`, `agents/`, and `sandbox/` are 100% byte-for-byte identical to baseline (proven via SHA-256 verification in `backend_files_hashes_baseline.csv`).
- **All existing features preserved**: Real-time WebSocket streaming, 9 cooperating swarm agents, AST risk heatmap, bug classification ledger, self-healing patch downloads, HTML reports, PR patch export, offline and online LLM model selectors, and custom snippet/zip project uploads.

---

## What Changed in UI v2

### 1. Light Design System
- **Palette**: Clean `#F4F6FA` dotted canvas background with `#FFFFFF` cards, `#E3E8F0` borders, `#0F172A` primary text, and `#5B6577` muted typography.
- **Color with Semantics**: Every color carries distinct meaning and is always accompanied by clear text labels:
  - Critical / Defect: Red (`#DC2626` / soft badge `#FEECEC`, text `#B42318`)
  - Verified / Success: Green (`#16A34A` / soft badge `#E7F8EE`, text `#14753B`)
  - Warning / Flaky: Amber (`#D97706` / soft badge `#FFF4E0`, text `#9A5B00`)
  - Info / Coverage: Blue (`#2563EB` / soft badge `#EAF1FF`, text `#1D4ED8`)
  - AI / Critic: Violet (`#7C3AED` / soft badge `#F1EAFE`, text `#6D28D9`)
- **Typography**: Manrope for headings, Inter for interface elements, and JetBrains Mono for telemetry, logs, and code. Complete system-font fallbacks for offline operation.

### 2. Layout Structure (Desktop 1440px, Responsive down to 768px)
- **A. Sticky Top Bar**: SentinelMesh branding, model selector chip with connection dot (Offline Engine, Gemini 2.5, OpenAI), and primary actions (*Run Demo Project*, *Analyze Code*, *Report (PR Patch)*, *Report (HTML)*).
- **B. Readiness Strip**: Live dynamic headline, circular SVG Suite Health ring, 5-item release gate (Verified Fixes, Coverage ≥80%, Mutation Score ≥60%, Zero Critical Open, Suite Health ≥75), plus quick action buttons (*Review the fix* and *Explain the bug*).
- **C. KPI Row**: 5 distinct metric cards: Bugs Found, Verified Fixes, Test Coverage, Mutation Score, and Suite Health.
- **D. Swarm & Telemetry (60/40 Split)**:
  - Left: **Live Agent Swarm** with interactive 2D Network Topology graph, a new **Flight Path** sequential pipeline view, and Report Agent phase indicator.
  - Right: **Telemetry & Agent Log** light console with level filtering (`ALL`, `INFO`, `WARN`, `ERROR`, `TELEMETRY`), per-agent filtering, auto-scroll pause toggle, and copy-to-clipboard.
- **E. Coverage Risk Heatmap**: File tiles sorted by risk score descending with LOC, Cyclomatic Complexity, and Security Smells. Clicking any module tile interactively filters the Bug Ledger to that file.
- **F. Bug Classification & Self-Healing Ledger**: Full-width interactive table with Location, Severity, Category, Defect Title, and Self-Healing status. Includes severity filter, category filter, full-text search box, and active row highlight.
- **G. Defect Explainer (Under Ledger)**:
  - Three navigation tabs: **Explain**, **Evidence** (actual failed test names, execution times, stack traces), and **Debate** (Critic Agent consensus rounds).
  - 3-box summary strip: *THE MISTAKE*, *THE IMPACT*, and *THE FIX*.
  - Left column: Code excerpt with red defect line bar, caret pointer (`^^^^`), and 3-step causal chain trace.
  - Right column: Corrected code with green safe lines, 3-point explanation of why the fix works, critic verification box, and actions (*Copy corrected code*, *Download patch (.patch)*, *Open PR patch*).
  - Beginner mode toggle: Translates technical AST diagnostics into plain-language analogies.
- **H. Critic Agent & Multi-Agent Debate**: Collapsible audit ledger formatted as a clean multi-agent message thread with consensus score meter.
- **I. Sticky Status Bar**: Real-time WebSocket connection liveness, Run ID copy button, and last synchronization timestamp.

---

## Changed Files
| File Path | Description of Changes |
| :--- | :--- |
| `frontend/index.html` | Converted to light theme, added Google Fonts (Manrope, Inter, JetBrains Mono) |
| `frontend/src/index.css` | Light design system CSS variables, dotted background utility, soft badge tokens |
| `frontend/src/constants.js` | Centralized `RELEASE_GATE_THRESHOLDS` constants block |
| `frontend/src/App.jsx` | Orchestrated 1440px desktop layout, connection banner, selection synchronization |
| `frontend/src/components/Header.jsx` | Light sticky top bar, model chip with connection dot, 4 primary actions |
| `frontend/src/components/ReadinessStrip.jsx` | New component: Circular health ring, 5-gate checklist, quick action triggers |
| `frontend/src/components/KPICards.jsx` | Light theme 5-card row with semantic color accents and trend indicators |
| `frontend/src/components/AgentNetworkGraph.jsx` | Light topology SVG, Network vs. Flight Path toggle, quick agent inspector |
| `frontend/src/components/LiveTerminal.jsx` | Light console, agent filter, level filter, pause scroll, copy log |
| `frontend/src/components/RiskHeatmap.jsx` | Risk-sorted module tiles, interactive filter callback to bug ledger |
| `frontend/src/components/BugExplorer.jsx` | Search box, severity/category filters, selection row highlight |
| `frontend/src/components/DefectExplainer.jsx` | New component: 3-box summary, carets, correct code, tabs (Explain/Evidence/Debate) |
| `frontend/src/components/AgentDebatePanel.jsx` | Collapsible multi-agent message thread with agreement verdicts |
| `frontend/src/components/StatusBar.jsx` | New component: Slim sticky bottom status bar with run ID copy and update clock |
| `frontend/src/components/NewProjectModal.jsx` | Light modal styling for snippet paste and zip upload |

---

## How to Run
Run the project exactly as before:
```powershell
.\run.ps1
```
Or with `run.bat` on Windows cmd:
```cmd
run.bat
```
The application will be available at `http://localhost:8000`.

---

## One-Step Rollback Instructions
To completely roll back all changes and return to the original interface:

### Option 1: Git Switch (Fastest)
```powershell
git checkout main
```

### Option 2: Restore Original Backup
A pristine, untouched backup of the original repository was preserved prior to edits:
`C:\Users\HARIESH\Downloads\S5 Mini Project_BACKUP_original`

To restore:
```powershell
robocopy "c:\Users\HARIESH\Downloads\S5 Mini Project_BACKUP_original" "c:\Users\HARIESH\Downloads\S5 Mini Project" /MIR /XD .git .venv node_modules
```
