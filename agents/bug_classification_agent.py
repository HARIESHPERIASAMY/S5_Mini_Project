"""
Bug Classification Agent for SentinelMesh.
Classifies bugs by severity, category, confidence score, and handles deduplication.
"""

import hashlib
import json
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentState
from backend.database import db_session_scope
from backend.models import Bug


class BugClassificationAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("bug_classification_agent", llm)

    async def run(self, run_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(run_id, AgentState.RUNNING, "Classifying and deduplicating detected bugs...")
        failed_tests = context.get("failed_tests", [])
        file_risks = context.get("file_risks", [])

        bugs = []
        seen_keys = set()

        # 1. Classify dynamic test failures
        for ft in failed_tests:
            target_file = ft.get("target_file", "unknown.py")
            test_name = ft.get("name", "test")
            err_msg = ft.get("error_message") or ""

            # Determine category & severity from error signature
            category, severity, title = self._classify_error(err_msg, test_name)
            dedup_key = hashlib.md5(f"{target_file}:{category}:{title}".encode("utf-8")).hexdigest()

            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            bug_item = {
                "file_path": target_file,
                "line_number": self._extract_line_number(err_msg),
                "title": title,
                "description": f"Test `{test_name}` failed: {err_msg[:300]}",
                "severity": severity,
                "category": category,
                "confidence": 0.95,
                "deduplication_key": dedup_key,
                "source": "DYNAMIC_TEST"
            }
            bugs.append(bug_item)

        # 2. Classify critical static smells (vulnerabilities that require attention)
        for fr in file_risks:
            smells = fr.get("smells_detail", [])
            for sm in smells:
                title = sm.get("title", "Static Vulnerability")
                desc = sm.get("desc", "")
                cat = "SECURITY" if "Security" in sm.get("type", "") else "LOGIC"
                sev = "HIGH" if cat == "SECURITY" else "MEDIUM"
                if "Dangerous" in title or "Zero" in title:
                    sev = "CRITICAL"

                dedup_key = hashlib.md5(f"{fr['file_path']}:{cat}:{title}".encode("utf-8")).hexdigest()
                if dedup_key in seen_keys:
                    continue
                seen_keys.add(dedup_key)

                bugs.append({
                    "file_path": fr["file_path"],
                    "line_number": sm.get("line", 1),
                    "title": title,
                    "description": desc,
                    "severity": sev,
                    "category": cat,
                    "confidence": 0.90,
                    "deduplication_key": dedup_key,
                    "source": "STATIC_ANALYSIS"
                })

        # Save bugs in database
        saved_bug_ids = []
        with db_session_scope() as session:
            for b in bugs:
                db_bug = Bug(
                    run_id=run_id,
                    file_path=b["file_path"],
                    line_number=b["line_number"],
                    title=b["title"],
                    description=b["description"],
                    severity=b["severity"],
                    category=b["category"],
                    confidence=b["confidence"],
                    deduplication_key=b["deduplication_key"],
                    fix_verified=False
                )
                session.add(db_bug)
                session.flush()
                b["id"] = db_bug.id
                saved_bug_ids.append(db_bug.id)

        await self.emit_telemetry(run_id, "bugs_count", len(bugs))
        await self.log(
            run_id,
            f"Classified {len(bugs)} distinct bugs (Critical: {sum(1 for b in bugs if b['severity'] == 'CRITICAL')}, High: {sum(1 for b in bugs if b['severity'] == 'HIGH')}).",
            "INFO"
        )

        await self.set_state(run_id, AgentState.COMPLETED)
        return {"bugs": bugs}

    def _classify_error(self, err_msg: str, test_name: str) -> (str, str, str):
        low = err_msg.lower() + " " + test_name.lower()
        if "zerodivision" in low or "division by zero" in low:
            return "LOGIC", "CRITICAL", "Unhandled ZeroDivisionError in arithmetic calculation"
        elif "sql" in low or "injection" in low:
            return "SECURITY", "CRITICAL", "SQL Injection vulnerability via unsanitized query parameters"
        elif "indexerror" in low or "off-by-one" in low or "out of range" in low:
            return "LOGIC", "HIGH", "Off-by-One Boundary Violation (IndexError)"
        elif "nonetype" in low or "attributeerror" in low or "has no attribute" in low:
            return "INPUT_VALIDATION", "HIGH", "Null Reference / NoneType Dereference Failure"
        elif "timeout" in low or "deadlock" in low or "race" in low:
            return "CONCURRENCY", "HIGH", "Concurrency Race Condition or Thread Deadlock"
        elif "valueerror" in low or "typeerror" in low:
            return "INPUT_VALIDATION", "MEDIUM", "Missing Input Type or Value Validation Guard"
        elif "flaky" in low:
            return "CONCURRENCY", "MEDIUM", "Non-Deterministic Flaky Test Behavior"
        else:
            return "LOGIC", "MEDIUM", f"Assertion Failure in `{test_name}`"

    def _extract_line_number(self, err_msg: str) -> int:
        import re
        match = re.search(r", line (\d+)", err_msg)
        if match:
            return int(match.group(1))
        return 1
