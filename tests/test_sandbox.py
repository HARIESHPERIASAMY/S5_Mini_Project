"""
Tests for Sandbox Runner and AST Mutation Engine.
"""

import os
import sys
import tempfile
import pytest
from sandbox.runner import SandboxRunner
from sandbox.mutator import MutationEngine


@pytest.mark.asyncio
async def test_sandbox_runner_basic():
    runner = SandboxRunner(timeout_sec=5.0)
    with tempfile.TemporaryDirectory() as tmpdir:
        res = await runner.run_command([sys.executable, "-c", "print('SentinelMesh')"], cwd=tmpdir)
        assert res.success is True
        assert "SentinelMesh" in res.stdout
        assert res.returncode == 0


@pytest.mark.asyncio
async def test_sandbox_runner_timeout():
    runner = SandboxRunner(timeout_sec=1.0)
    with tempfile.TemporaryDirectory() as tmpdir:
        res = await runner.run_command(
            [sys.executable, "-c", "import time; time.sleep(3)"],
            cwd=tmpdir,
            timeout=1.0
        )
        assert res.timed_out is True
        assert res.success is False


def test_mutation_engine_discovery():
    mutator = MutationEngine()
    code = """
def is_valid(x, y):
    if x == y and x > 0:
        return True
    return False
"""
    mutants = mutator.discover_mutants(code)
    assert len(mutants) > 0
    types = [m[0].mut_type for m in mutants]
    assert "COMPARE_OP" in types or "BOOLEAN_FLIP" in types
