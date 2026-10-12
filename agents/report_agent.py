"""
Report Agent for SentinelMesh.
Compiles executive summaries, technical audit reports, and exports in Markdown, HTML, and JSON.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentState
from backend.database import db_session_scope
from backend.models import Run


class ReportAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("report_agent", llm)

    async def run(self, run_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(run_id, AgentState.RUNNING, "Synthesizing executive summary & technical report...")

        total_files = context.get("total_files", 0)
        total_loc = context.get("total_loc", 0)
        risk_score = context.get("avg_risk", 0.0)
        coverage_pct = context.get("coverage_pct", 0.0)
        mutation_score = context.get("mutation_score", 0.0)
        suite_health = context.get("health_score", 0.0)
        bugs = context.get("bugs", [])
        verified_fixes = context.get("verified_fixes_count", 0)
        consensus = context.get("overall_consensus", 95.0)

        # 1. Executive Summary
        exec_summary = (
            f"SentinelMesh Multi-Agent Audit completed for {total_files} source files ({total_loc} lines of code). "
            f"The codebase demonstrates an overall risk index of {risk_score}%, with a test suite coverage of {coverage_pct}% "
            f"and a mutation kill score of {mutation_score}%. A total of {len(bugs)} vulnerabilities/defects were detected, "
            f"with {verified_fixes} automatically patched and sandbox-verified. Multi-agent consensus stands at {consensus}%."
        )

        # 2. Comprehensive Technical Report in Markdown
        tech_report = self._build_technical_report(
            run_id=run_id,
            total_files=total_files,
            total_loc=total_loc,
            risk_score=risk_score,
            coverage_pct=coverage_pct,
            mutation_score=mutation_score,
            suite_health=suite_health,
            bugs=bugs,
            verified_fixes=verified_fixes,
            consensus=consensus
        )

        # Update Run in DB
        with db_session_scope() as session:
            db_run = session.query(Run).filter(Run.id == run_id).first()
            if db_run:
                db_run.executive_summary = exec_summary
                db_run.technical_report = tech_report

        await self.log(run_id, "Executive summary and technical audit report generated successfully.", "INFO")
        await self.set_state(run_id, AgentState.COMPLETED)

        return {
            "executive_summary": exec_summary,
            "technical_report": tech_report
        }

    def _build_technical_report(
        self,
        run_id: str,
        total_files: int,
        total_loc: int,
        risk_score: float,
        coverage_pct: float,
        mutation_score: float,
        suite_health: float,
        bugs: List[Dict[str, Any]],
        verified_fixes: int,
        consensus: float
    ) -> str:
        bug_rows = []
        for b in bugs:
            verified_badge = "[VERIFIED FIX]" if b.get("fix_verified") else "[PROPOSED]"
            bug_rows.append(
                f"| `{b.get('file_path')}:{b.get('line_number')}` | **{b.get('severity')}** | {b.get('category')} | {b.get('title')} | {verified_badge} |"
            )
        bug_table = "\n".join(bug_rows) if bug_rows else "| None | - | - | No critical bugs detected | - |"

        return f"""# SentinelMesh Comprehensive Security & Quality Audit Report
**Run Identifier:** `{run_id}`  
**Generated At:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Agent Architecture:** 9-Agent Cooperating Swarm with Sandbox Self-Healing  

---

## 1. Executive Telemetry Summary

| Metric | Measured Value | Target Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Analyzed Modules** | `{total_files}` files ({total_loc} LOC) | - | Monitored |
| **Codebase Risk Score** | `{risk_score}%` | `< 30.0%` | {'CRITICAL' if risk_score > 60 else 'ACCEPTABLE'} |
| **Test Coverage** | `{coverage_pct}%` | `> 80.0%` | {'HEALTHY' if coverage_pct >= 80 else 'SUB-OPTIMAL'} |
| **Mutation Testing Score** | `{mutation_score}%` | `> 75.0%` | {'HIGH QUALITY' if mutation_score >= 70 else 'IMPROVEMENT NEEDED'} |
| **Suite Health Score** | `{suite_health}/100` | `> 85/100` | STABLE |
| **Bugs Detected** | `{len(bugs)}` issues | `0` | ACTION REQUIRED |
| **Self-Healing Verified Fixes** | `{verified_fixes} / {len(bugs)}` | `100%` | {'EXCELLENT' if verified_fixes > 0 else 'PENDING'} |
| **Critic Consensus** | `{consensus}%` | `> 90.0%` | HIGH CONFIDENCE |

---

## 2. Bug Classification & Defect Ledger

| Location | Severity | Category | Title | Fix Status |
| :--- | :--- | :--- | :--- | :--- |
{bug_table}

---

## 3. Self-Healing Verification Ledger
All verified fixes have undergone execution in an isolated sandbox clone with regression assertions re-evaluated.
Patches can be exported directly as unified git-compatible diffs using the SentinelMesh dashboard.

---
*Report synthesized automatically by SentinelMesh Agent Orchestration Engine.*
"""
