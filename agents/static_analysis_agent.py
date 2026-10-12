"""
Static Analysis Agent for SentinelMesh.
Performs AST parsing, complexity calculation, security smells detection,
and produces a per-file Risk Score to drive prioritized test generation.
"""

import ast
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentState
from backend.database import db_session_scope
from backend.models import FileRisk


class StaticAnalysisAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("static_analysis_agent", llm)

    async def run(self, run_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(run_id, AgentState.RUNNING, "Starting AST & complexity scanning...")
        workspace_dir = context.get("workspace_dir")
        if not workspace_dir or not os.path.exists(workspace_dir):
            await self.log(run_id, "No valid workspace directory for static analysis.", "ERROR")
            await self.set_state(run_id, AgentState.FAILED)
            return {"file_risks": []}

        python_files = self._collect_python_files(workspace_dir)
        await self.log(run_id, f"Discovered {len(python_files)} Python source files to inspect.", "INFO")

        file_risks = []
        total_loc = 0

        for rel_path in python_files:
            abs_path = os.path.join(workspace_dir, rel_path)
            try:
                with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                    code = f.read()
            except Exception as e:
                await self.log(run_id, f"Could not read {rel_path}: {e}", "WARN")
                continue

            loc = len([line for line in code.splitlines() if line.strip() and not line.strip().startswith("#")])
            total_loc += loc

            # AST & Radon Complexity
            complexity = self._calculate_complexity(code)

            # Security and Code Smells
            smells = self._detect_smells_and_vulnerabilities(code, rel_path)

            # Risk Score Formula (0 to 100)
            # Complexity weight: 4.0 pts per CC above 1, capped at 40
            # Security smell weight: 15.0 pts per smell, capped at 45
            # LOC density weight: min(15, loc // 20)
            comp_pts = min(40.0, max(0.0, (complexity - 1.0) * 4.0))
            smell_pts = min(45.0, len(smells) * 15.0)
            loc_pts = min(15.0, (loc / 50.0) * 15.0)

            risk_score = round(min(100.0, max(5.0, comp_pts + smell_pts + loc_pts)), 1)

            if risk_score >= 70:
                risk_level = "CRITICAL"
            elif risk_score >= 45:
                risk_level = "HIGH"
            elif risk_score >= 25:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            risk_item = {
                "file_path": rel_path,
                "loc": loc,
                "cyclomatic_complexity": complexity,
                "security_smells": len(smells),
                "risk_score": risk_score,
                "risk_level": risk_level,
                "smells_detail": smells
            }
            file_risks.append(risk_item)

            # Save in database
            with db_session_scope() as session:
                fr_rec = FileRisk(
                    run_id=run_id,
                    file_path=rel_path,
                    loc=loc,
                    cyclomatic_complexity=complexity,
                    security_smells=len(smells),
                    risk_score=risk_score,
                    risk_level=risk_level,
                    details=json.dumps(smells)
                )
                session.add(fr_rec)

            await self.log(
                run_id,
                f"[{risk_level}] {rel_path} -> Complexity: {complexity}, Smells: {len(smells)}, Risk: {risk_score}%",
                "INFO"
            )

        # Sort files by risk score descending (prioritize high risk)
        file_risks.sort(key=lambda x: x["risk_score"], reverse=True)

        avg_risk = round(sum(f["risk_score"] for f in file_risks) / len(file_risks), 1) if file_risks else 0.0
        await self.emit_telemetry(run_id, "risk_score", avg_risk)
        await self.emit_telemetry(run_id, "lines_of_code", total_loc)
        await self.emit_telemetry(run_id, "total_files", len(file_risks))

        await self.set_state(run_id, AgentState.COMPLETED, f"Analysis complete. Codebase average risk: {avg_risk}%")
        return {
            "file_risks": file_risks,
            "total_loc": total_loc,
            "avg_risk": avg_risk
        }

    def _collect_python_files(self, workspace_dir: str) -> List[str]:
        collected = []
        for root, dirs, files in os.walk(workspace_dir):
            dirs[:] = [d for d in dirs if d not in (".git", "venv", ".venv", "__pycache__", ".pytest_cache", "tests")]
            for f in files:
                if f.endswith(".py") and not f.startswith("test_"):
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, workspace_dir).replace("\\", "/")
                    collected.append(rel)
        return collected

    def _calculate_complexity(self, code: str) -> float:
        """Calculates cyclomatic complexity using AST branch counting."""
        try:
            tree = ast.parse(code)
            branches = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With)):
                    branches += 1
                elif isinstance(node, ast.BoolOp):
                    branches += len(node.values) - 1
            return float(branches)
        except Exception:
            return 1.0

    def _detect_smells_and_vulnerabilities(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        smells = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # 1. Zero Division risk
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    smells.append({
                        "line": node.lineno,
                        "type": "ArithmeticRisk",
                        "title": "Division Operation Without Zero Check",
                        "desc": "Division operand may trigger ZeroDivisionError if denominator evaluates to 0."
                    })
                # 2. SQL injection pattern
                if isinstance(node, ast.Call):
                    name = ""
                    if isinstance(node.func, ast.Attribute):
                        name = node.func.attr
                    elif isinstance(node.func, ast.Name):
                        name = node.func.id
                    if name in ("execute", "raw_query", "query"):
                        for arg in node.args:
                            if isinstance(arg, ast.JoinedStr) or (isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod)):
                                smells.append({
                                    "line": node.lineno,
                                    "type": "SecurityVulnerability",
                                    "title": "SQL Injection Risk (String Interpolation)",
                                    "desc": f"Call to `{name}` formats query strings dynamically instead of parameter binding."
                                })
                # 3. Bare except
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        smells.append({
                            "line": node.lineno,
                            "type": "CodeSmell",
                            "title": "Bare Except Clause",
                            "desc": "Catching all exceptions silently masks critical runtime errors and keyboard interrupts."
                        })
                # 4. Dangerous eval / exec
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ("eval", "exec"):
                        smells.append({
                            "line": node.lineno,
                            "type": "CriticalSecurityVulnerability",
                            "title": f"Dangerous Code Execution via `{node.func.id}()`",
                            "desc": f"Direct invocation of `{node.func.id}()` allows arbitrary code execution."
                        })
        except SyntaxError as e:
            smells.append({
                "line": e.lineno or 1,
                "type": "SyntaxError",
                "title": "Python Syntax Error",
                "desc": str(e)
            })

        return smells
