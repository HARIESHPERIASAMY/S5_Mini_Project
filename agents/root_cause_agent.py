"""
Root Cause Agent for SentinelMesh.
Traces failure back to the exact code line, constructs causal chains,
and synthesizes beginner-friendly explanations.
"""

import json
import os
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentState
from backend.database import db_session_scope
from backend.models import Bug


class RootCauseAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("root_cause_agent", llm)

    async def run(self, run_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(run_id, AgentState.RUNNING, "Synthesizing causal chains and root causes...")
        bugs = context.get("bugs", [])
        workspace_dir = context.get("workspace_dir")

        if not bugs:
            await self.set_state(run_id, AgentState.COMPLETED, "No bugs to analyze.")
            return {"bugs": []}

        analyzed_bugs = []
        for bug in bugs:
            file_path = bug.get("file_path", "")
            abs_path = os.path.join(workspace_dir, file_path) if workspace_dir else ""
            line_no = bug.get("line_number", 1)

            source_snippet = ""
            if os.path.exists(abs_path):
                try:
                    with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                        start = max(0, line_no - 4)
                        end = min(len(lines), line_no + 4)
                        source_snippet = "".join(lines[start:end])
                except Exception:
                    pass

            await self.log(run_id, f"Tracing causal chain for: {bug['title']} ({file_path}:{line_no})", "INFO")

            # Build causal chain steps
            causal_chain = self._build_causal_chain(bug, line_no, source_snippet)

            # Generate Beginner Explanation
            beginner_exp = await self.llm.explain_bug(
                bug_title=bug["title"],
                code_snippet=source_snippet,
                causal_chain=causal_chain
            )

            bug["causal_chain"] = json.dumps(causal_chain)
            bug["beginner_explanation"] = beginner_exp
            analyzed_bugs.append(bug)

            # Update Bug in DB
            bug_id = bug.get("id")
            if bug_id:
                with db_session_scope() as session:
                    db_bug = session.query(Bug).filter(Bug.id == bug_id).first()
                    if db_bug:
                        db_bug.causal_chain = json.dumps(causal_chain)
                        db_bug.beginner_explanation = beginner_exp

        await self.set_state(run_id, AgentState.COMPLETED, f"Root causes determined for {len(analyzed_bugs)} bugs.")
        return {"bugs": analyzed_bugs}

    def _build_causal_chain(self, bug: Dict[str, Any], line_no: int, snippet: str) -> List[str]:
        title = bug.get("title", "").lower()
        cat = bug.get("category", "")

        if "zerodivision" in title or "division" in title:
            return [
                "1. Caller invokes arithmetic routine with an edge-case denominator (e.g. rate = 0).",
                f"2. Execution arrives at line {line_no} without checking if the divisor is zero.",
                "3. Python runtime evaluates `x / 0`, raising a fatal `ZeroDivisionError` exception.",
                "4. Unhandled exception propagates up the call stack, crashing the request pipeline."
            ]
        elif "sql" in title or cat == "SECURITY":
            return [
                "1. External user input is passed directly into a database query string.",
                f"2. At line {line_no}, an f-string or string formatting embeds unescaped characters.",
                "3. The database parser interprets injected syntax as SQL command instructions.",
                "4. Vulnerability allows unauthorized data exfiltration or table tampering."
            ]
        elif "indexerror" in title or "boundary" in title or "off-by-one" in title:
            return [
                "1. Input collection size is compared with an inclusive boundary (e.g. `<= len(items)`).",
                f"2. Loop or array index at line {line_no} accesses `items[len(items)]`.",
                "3. Array indexes in Python are 0-indexed, so the highest element index is `len(items) - 1`.",
                "4. Access causes an `IndexError: list index out of range` failure."
            ]
        elif "none" in title or cat == "INPUT_VALIDATION":
            return [
                "1. Method receives an empty, null, or uninitialized object parameter.",
                f"2. At line {line_no}, code accesses an attribute or method directly (e.g. `obj.strip()`).",
                "3. Because `obj` is `None`, Python raises `AttributeError: 'NoneType' object has no attribute`.",
                "4. Missing defensive guard check prevents safe degradation or user feedback."
            ]
        else:
            return [
                "1. Execution enters target function under non-standard boundary arguments.",
                f"2. Logic condition at line {line_no} evaluates incorrectly.",
                "3. The return state violates expected assertion contract.",
                "4. Automated test suite detects regression and halts execution."
            ]
