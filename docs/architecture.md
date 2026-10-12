# SentinelMesh: Technical Architecture & System Design Document

**Platform:** SentinelMesh — Intelligent Multi-Agent Software Testing and Bug Analysis Platform  
**Version:** 1.0.0 (Production-Grade Swarm Architecture)  
**Author:** SentinelMesh Principal Architecture Team  

---

## 1. Executive Architecture Overview

SentinelMesh is an autonomous, multi-agent quality engineering system designed to analyze software repositories, discover latent defects, synthesize boundary test suites, trace causal root causes, and automatically verify proposed fixes in an isolated sandbox.

```
                          +---------------------------------------------------+
                          |            Mission-Control Dashboard              |
                          |   (React 19 + Vite + Tailwind + Framer Motion)    |
                          +-------------------------+-------------------------+
                                                    |
                                       HTTP REST & WebSocket Stream
                                                    |
                          +-------------------------v-------------------------+
                          |                 FastAPI Gateway                   |
                          |      Async In-Memory Event Bus & DB Layer         |
                          +-------------------------+-------------------------+
                                                    |
            +---------------------------------------v---------------------------------------+
            |                        SentinelMesh Orchestrator Swarm                        |
            |                         Directed Acyclic Graph (DAG)                          |
            +---+-------------------+-------------------+-------------------+---------------+
                |                   |                   |                   |               |
                |                   |                   |                   |               |
    +-----------v-----------+       |                   |                   |   +-----------v-----------+
    | Static Analysis Agent |       |                   |                   |   |     Report Agent      |
    | (AST + Radon + Smells)|       |                   |                   |   | (Executive & Markdown)|
    +-----------+-----------+       |                   |                   |   +-----------^-----------+
                |                   |                   |                   |               |
    +-----------v-----------+       |                   |                   |   +-----------+-----------+
    | Test Generation Agent |       |                   |                   |   |     Critic Agent      |
    | (Unit + Boundary + EL)|       |                   |                   |   | (Debate & Consensus)  |
    +-----------+-----------+       |                   |                   |   +-----------^-----------+
                |                   |                   |                   |               |
    +-----------v-----------+       |                   |                   |   +-----------+-----------+
    | Test Execution Agent  +-------+                   |                   +---+   Auto-Fix Agent      |
    | (Coverage + Flakiness)|                           |                       | (Diffs & Re-verif)    |
    +-----------+-----------+                           |                       +-----------^-----------+
                |                                       |                                   |
    +-----------v-----------+                           |                       +-----------+-----------+
    | Bug Classifier Agent  +---------------------------+-----------------------+   Root Cause Agent    |
    | (Severity & Category) |                                                   | (Causal Trace & ELI5) |
    +-----------------------+                                                   +-----------------------+
                                                        |
                                            +-----------v-----------+
                                            |  AST Mutation Engine  |
                                            | (Operator Inversion)  |
                                            +-----------+-----------+
                                                        |
                                            +-----------v-----------+
                                            |   Subprocess Sandbox  |
                                            | (Isolated Temp Clones)|
                                            +-----------------------+
```

---

## 2. Multi-Agent Swarm Specification (9 Cooperating Agents)

### 1. Orchestrator Agent (`agents/orchestrator_agent.py`)
- **Role:** Central mission coordinator.
- **Responsibilities:**
  - Manages the execution pipeline state machine: `IDLE` -> `THINKING` -> `RUNNING` -> `COMPLETED` / `FAILED`.
  - Dispatches tasks across the other 8 specialized agents with dependency checks and error recovery.
  - Broadcasts global progress percentages (0% to 100%) and current agent indicators over WebSockets.

### 2. Static Analysis Agent (`agents/static_analysis_agent.py`)
- **Role:** Structural auditor and early risk evaluator.
- **Responsibilities:**
  - AST-based inspection of Python modules (discovers unguarded zero-divisions, bare `except:` clauses, unsafe `eval`/`exec`, and dynamic string-formatted SQL queries).
  - Computes cyclomatic branch complexity.
  - Computes the file-level **Risk Score** (0 to 100%):
    $$\text{Risk Score} = \min(100, \max(5, \text{Complexity Pts} + \text{Smell Pts} + \text{LOC Density Pts}))$$
  - Sorts codebase modules in descending risk order to drive **Risk-Prioritized Testing**.

### 3. Test Generation Agent (`agents/test_generation_agent.py`)
- **Role:** Autonomous test case synthesizer.
- **Responsibilities:**
  - Ingests modules prioritized by risk score.
  - Inspects function signatures, parameter names, and AST call patterns.
  - Generates comprehensive `pytest` test suites covering:
    - Nominal behavior tests.
    - Boundary and edge-case inputs (e.g., `0`, `-1`, `""`, `[]`).
    - Null-safety checks (`None` dereference validation).
    - Exception contract verifications.

### 4. Test Execution Agent (`agents/test_execution_agent.py`)
- **Role:** Sandboxed dynamic test runner and telemetry collector.
- **Responsibilities:**
  - Executes generated test suites within an isolated subprocess with strict timeouts.
  - Runs `coverage.py` to calculate line and branch coverage percentages.
  - **Flaky Test Detector:** Automatically re-runs failed or non-deterministic tests 3 times with jitter to identify race conditions vs persistent regressions.
  - Computes **Test Suite Health Score (0-100)**:
    $$\text{Health} = (\text{Pass Rate} \times 0.5) + (\text{Coverage} \times 0.5) - \text{Flakiness Penalty}$$

### 5. Bug Classification Agent (`agents/bug_classification_agent.py`)
- **Role:** Defect categorization and deduplication engine.
- **Responsibilities:**
  - Merges dynamic execution failures with high-severity static vulnerabilities.
  - Classifies severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
  - Classifies category: `LOGIC`, `SECURITY`, `PERFORMANCE`, `CONCURRENCY`, `INPUT_VALIDATION`.
  - Generates deterministic MD5 deduplication keys to eliminate duplicate error reports across iterations.

### 6. Root Cause Agent (`agents/root_cause_agent.py`)
- **Role:** Forensic backtracker and conceptual explainer.
- **Responsibilities:**
  - Correlates test failure stack traces with AST source code line numbers.
  - Constructs a step-by-step **Causal Chain** explaining the chain of events that triggered the failure.
  - Produces an **"Explain Like I'm a Beginner" (ELI5)** explanation using intuitive real-world analogies.

### 7. Auto-Fix Agent (`agents/auto_fix_agent.py`)
- **Role:** Autonomous patch generator with self-healing verification.
- **Responsibilities:**
  - Synthesizes unified git-compatible diff patches (`diff -u`).
  - **Self-Healing Verification Loop:** Clones the codebase into a clean, isolated temporary sandbox, applies the proposed diff patch, and re-executes the regression test suite.
  - Only awards the **`[VERIFIED FIX]`** badge when sandbox test re-execution passes with zero regressions!

### 8. Critic / Reviewer Agent (`agents/critic_agent.py`)
- **Role:** Hallucination filter and adversarial debate arbiter.
- **Responsibilities:**
  - Evaluates findings from Static Analysis and Bug Classification.
  - Challenges borderline findings and identifies false positives.
  - Engages in structured debate rounds with claiming agents.
  - Computes the swarm **Consensus Score** (0 to 100%).

### 9. Report Agent (`agents/report_agent.py`)
- **Role:** Audit synthesizer and exporter.
- **Responsibilities:**
  - Aggregates metrics from all 8 upstream agents.
  - Generates an Executive Summary and comprehensive Markdown/HTML technical reports.
  - Enables 1-click export of PR-ready patch bundles.

---

## 3. Innovative Highlights

### Self-Healing Loop
```
[Generate Tests] -> [Execute Sandbox] -> [Capture Failure] -> [Trace Root Cause]
       ^                                                                |
       |                                                                v
[Award Verified Badge] <-- [Test Suite Green] <-- [Sandbox Re-Run] <-- [Apply Diff Patch]
```

### AST Mutation Testing Engine
To verify the actual efficacy of generated test suites (beyond passive line coverage), SentinelMesh includes an AST-driven mutation engine (`sandbox/mutator.py`):
1. Traverses the abstract syntax tree and applies deliberate operator inversions:
   - Comparison: `==` $\leftrightarrow$ `!=`, `<` $\leftrightarrow$ `>=`, `in` $\leftrightarrow$ `not in`
   - Arithmetic: `+` $\leftrightarrow$ `-`, `*` $\leftrightarrow$ `/`
   - Booleans: `True` $\leftrightarrow$ `False`
2. Runs the test suite against each generated mutant.
3. If the test suite fails, the mutant is **KILLED** (high test sensitivity). If the test suite passes, the mutant **SURVIVED** (uncovered test logic gap).
4. Calculates Mutation Kill Score:
   $$\text{Mutation Score} = \frac{\text{Mutants Killed}}{\text{Total Mutants}} \times 100\%$$

---

## 4. Subprocess Isolation & Security Guards

1. **Subprocess Sandboxing:** Commands (`pytest`, `coverage`, patches) execute in isolated subprocesses using `asyncio.subprocess` with enforced timeouts (8s to 20s).
2. **Workspace Cloning:** Fixes are verified inside isolated temporary directories (`tempfile.mkdtemp()`) without contaminating user workspace files.
3. **Clean Environment:** Subprocesses execute with sanitized environment variables and `PYTHONDONTWRITEBYTECODE=1`.

---

## 5. Offline Operation & Pluggable LLM Layer

SentinelMesh provides a pluggable provider interface (`backend/llm/base.py`):
- **Offline Mode (Default):** Runs 100% locally with zero API keys and zero internet access using rule heuristics and AST pattern analyzers.
- **Google Gemini Provider:** Automatically activates when `GEMINI_API_KEY` is detected, falling back to offline mode on network interruptions.
- **OpenAI / Ollama Provider:** Supports OpenAI models or local self-hosted models running via Ollama (`http://localhost:11434/v1`).
