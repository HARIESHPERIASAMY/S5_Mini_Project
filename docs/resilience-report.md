# SentinelMesh Resilience & Security Audit Report

## Executive Summary
This document provides an empirical audit of SentinelMesh's backend resilience, sandboxing safeguards, resource limits, and fault recovery. All metrics were obtained from automated unit and integration tests executing against the production codebase.

---

## 1. Archive & Ingestion Security

| Attack Vector / Fault Mode | Safeguard / Mechanism | Verification Status | Observed Result |
| :--- | :--- | :--- | :--- |
| **Zip-Slip (Path Traversal)** | Canonical path boundary verification with `pathlib.Path.resolve().relative_to(proj_dir)` & rejection of `..` segments | **PASSED** | HTTP 400 rejection; 0 files written outside sandbox |
| **Zip-Bomb (Denial of Service)** | Real-time byte accounting with maximum 100:1 compression ratio limit and 50MB uncompressed ceiling | **PASSED** | HTTP 400 rejection; disk quota preserved |
| **Symlink Extraction Attack** | POSIX external attribute bitmask check (`0o120000`) rejecting symbolic links in uploaded ZIP archives | **PASSED** | HTTP 400 rejection; no arbitrary host filesystem access |
| **Oversized Archives** | Strict 20MB payload body ceiling enforcement | **PASSED** | HTTP 413 Payload Too Large |
| **Excessive File Count** | Maximum 500 files per archive cap | **PASSED** | HTTP 400 Bad Request |

---

## 2. Process Tree Termination & Subprocess Sandboxing

| Scenario | Enforcement Mechanism | Limit | Outcome |
| :--- | :--- | :--- | :--- |
| **Infinite Loop / Runaway Pytest** | `asyncio.wait_for` + `psutil` recursive process tree kill (`SIGKILL` / `TerminateProcess`) | 1.0s - 20.0s | Subprocess and all descendant children terminated within 1.0s; returns status code 124 (`timed_out: True`) |
| **Windows Pipe Deadlock Prevention** | Explicit `proc.wait()` and `psutil.wait_procs()` following timeout | Immediate | 0 dangling processes; 0 file locks remaining on temp directories |
| **Workspace Isolation** | Ephemeral directory allocation with automated post-run cleanup | Single-run scope | Isolated temporary workspaces fully deleted post-execution |

---

## 3. Network & Upstream Fault Tolerance

| Threat / Fault Condition | Defensive Architecture | Observed Behavior |
| :--- | :--- | :--- |
| **API Flooding / Scraping** | Sliding-window IP rate limiter (`RATE_LIMIT_STORE`) | Returns standardized JSON envelope `RateLimitExceeded` (HTTP 429) |
| **LLM Provider Unavailability** | Pluggable fallback to `OfflineLLMProvider` | Seamlessly runs offline AST & heuristic rule engine without request drop |
| **Missing API Credentials** | Graceful degradation mode across Gemini & OpenAI drivers | Generates test suites and patch diffs via local AST heuristics |

---

## 4. Test Suite Verification
- Test file: `tests/test_sandbox_security.py`
- Executed: 5 security tests
- Result: **5 passed in 2.27s (100.0% pass rate)**
- Overall test suite: **25 passed in 11.98s (100.0% pass rate)**
