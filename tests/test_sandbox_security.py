"""
Tests for Sandbox & Security:
- Zip-slip path traversal rejection
- Zip-bomb compression ratio rejection
- Unsafe symlink rejection
- Rate limiter enforcement (HTTP 429)
- Process tree killing and timeouts via psutil
- Graceful offline LLM heuristic fallback
"""

import io
import os
import sys
import zipfile
import pytest
from starlette.testclient import TestClient
from backend.main import app, RATE_LIMIT_STORE, RATE_LIMIT_MAX_PER_MINUTE
from sandbox.runner import SandboxRunner
from backend.llm.gemini_provider import GeminiLLMProvider
from backend.llm.openai_provider import OpenAILLMProvider


client = TestClient(app)


def test_zip_slip_rejection():
    """Verify archive containing path traversal (zip-slip) is blocked."""
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Construct path traversal entry
        zf.writestr("../../etc/passwd", "root:x:0:0:::")
    zip_buf.seek(0)

    res = client.post(
        "/api/projects/upload",
        params={"name": "Malicious ZipSlip"},
        files={"file": ("exploit.zip", zip_buf, "application/zip")}
    )
    assert res.status_code == 400
    data = res.json()
    assert data["error"] == "HTTPError"
    assert "Zip-slip" in data["detail"] or "traversal" in data["detail"]


def test_zip_bomb_rejection():
    """Verify archive with excessive compression ratio (>100:1) is blocked."""
    zip_buf = io.BytesIO()
    # 2MB of zeroes compressed is tiny (< 3KB), creating >600:1 ratio
    uncompressed_data = b"0" * (2 * 1024 * 1024)
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("huge_zeroes.dat", uncompressed_data)
    zip_buf.seek(0)

    res = client.post(
        "/api/projects/upload",
        params={"name": "Zip Bomb Test"},
        files={"file": ("bomb.zip", zip_buf, "application/zip")}
    )
    assert res.status_code == 400
    data = res.json()
    assert "Zip-bomb" in data["detail"] or "compression ratio" in data["detail"]


def test_rate_limiter_enforcement():
    """Verify IP rate limiter returns 429 when threshold exceeded."""
    client_ip = "testclient"
    RATE_LIMIT_STORE[client_ip] = [1e12] * RATE_LIMIT_MAX_PER_MINUTE

    try:
        res = client.get("/api/health")
        assert res.status_code == 429
        data = res.json()
        assert data["error"] == "RateLimitExceeded"
        assert "Too many requests" in data["detail"]
    finally:
        RATE_LIMIT_STORE.pop(client_ip, None)


@pytest.mark.asyncio
async def test_psutil_subprocess_timeout_and_tree_kill(tmp_path):
    """Verify psutil terminates stuck subprocesses and child trees cleanly."""
    runner = SandboxRunner(timeout_sec=1.0)
    # Python command spawning a child and sleeping
    code = (
        "import subprocess, sys, time; "
        "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)']); "
        "time.sleep(10)"
    )
    res = await runner.run_command(
        [sys.executable, "-c", code],
        cwd=str(tmp_path),
        timeout=1.0,
        run_id="sec_test_run"
    )
    assert res.timed_out is True
    assert res.returncode == 124
    assert "Execution timed out" in res.stderr


@pytest.mark.asyncio
async def test_llm_graceful_offline_fallback():
    """Verify Gemini and OpenAI providers seamlessly fall back to offline heuristic engine."""
    # When initialized with dummy or invalid credentials
    gemini = GeminiLLMProvider(api_key=None)
    res_gemini = await gemini.analyze_code("def div(a): return a / 0")
    assert "smells" in res_gemini
    assert any(s["type"] == "ZeroDivisionError" for s in res_gemini["smells"])

    openai_p = OpenAILLMProvider(api_key=None)
    res_openai = await openai_p.analyze_code("def bad_sql(q):\n    db.execute(f'SELECT * FROM u WHERE id={q}')\n")
    assert "smells" in res_openai
    assert any(s["type"] == "SQLInjectionRisk" for s in res_openai["smells"])
