"""
Test Generation Agent for SentinelMesh.
Produces prioritized pytest test suites covering unit, edge-case, boundary,
and property-based tests based on file risk scores.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentState


class TestGenerationAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("test_generation_agent", llm)

    async def run(self, run_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.set_state(run_id, AgentState.RUNNING, "Synthesizing prioritized test suites...")
        workspace_dir = context.get("workspace_dir")
        file_risks = context.get("file_risks", [])

        if not workspace_dir or not os.path.exists(workspace_dir):
            await self.set_state(run_id, AgentState.FAILED, "Invalid workspace directory.")
            return {"generated_tests": []}

        tests_dir = os.path.join(workspace_dir, "sentinel_tests")
        os.makedirs(tests_dir, exist_ok=True)
        # Create __init__.py so pytest can import modules cleanly
        init_file = os.path.join(tests_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write('"""SentinelMesh Generated Test Suite"""\n')

        generated_test_files = []

        # Iterate over files in order of highest risk
        for item in file_risks:
            rel_file = item["file_path"]
            abs_file = os.path.join(workspace_dir, rel_file)
            if not os.path.exists(abs_file):
                continue

            try:
                with open(abs_file, "r", encoding="utf-8", errors="replace") as f:
                    source_code = f.read()
            except Exception as e:
                await self.log(run_id, f"Error reading {rel_file}: {e}", "WARN")
                continue

            base_name = os.path.basename(rel_file).replace(".py", "")
            test_filename = f"test_{base_name}.py"
            test_path = os.path.join(tests_dir, test_filename)
            rel_test_path = os.path.relpath(test_path, workspace_dir).replace("\\", "/")

            await self.log(
                run_id,
                f"Synthesizing unit and boundary tests for {rel_file} (Risk: {item['risk_score']}%)...",
                "INFO"
            )

            # Generate test code via LLM / Offline provider
            test_code = await self.llm.generate_tests(
                code=source_code,
                filename=rel_file,
                context={"risk_level": item["risk_level"], "smells": item.get("smells_detail", [])}
            )

            # Ensure workspace directory is in sys.path in test file
            header = (
                "import sys, os\n"
                f"sys.path.insert(0, os.path.abspath('{workspace_dir.replace(chr(92), '/')}'))\n"
            )
            final_test_code = header + "\n" + test_code

            try:
                with open(test_path, "w", encoding="utf-8") as tf:
                    tf.write(final_test_code)
                generated_test_files.append({
                    "target_file": rel_file,
                    "test_file": rel_test_path,
                    "test_abs_path": test_path
                })
                await self.log(run_id, f"Generated test suite written to: {rel_test_path}", "INFO")
            except Exception as e:
                await self.log(run_id, f"Failed writing test file {rel_test_path}: {e}", "ERROR")

        await self.set_state(run_id, AgentState.COMPLETED, f"Generated {len(generated_test_files)} test suites.")
        return {
            "generated_tests": generated_test_files,
            "tests_dir": tests_dir
        }
