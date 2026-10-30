"""
Sandbox Execution Manager for SentinelMesh.
Runs tests and processes in isolated subprocesses with strict timeouts,
process tree killing via psutil, and workspace isolation.
"""

import asyncio
import os
import shutil
import tempfile
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
import psutil


class SandboxResult:
    def __init__(
        self,
        returncode: int,
        stdout: str,
        stderr: str,
        duration_ms: float,
        timed_out: bool = False,
        memory_mb: float = 0.0
    ):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.timed_out = timed_out
        self.memory_mb = memory_mb

    @property
    def success(self) -> bool:
        return self.returncode == 0 and not self.timed_out


class SandboxRunner:
    MAX_OUTPUT_BYTES = 512 * 1024  # 512 KB output cap
    MAX_MEMORY_MB = 256.0           # 256 MB memory limit

    def __init__(self, timeout_sec: float = 20.0):
        self.timeout_sec = timeout_sec
        # run_id -> set of active process PIDs
        self._active_pids: Dict[str, Set[int]] = {}
        self._lock = asyncio.Lock()

    async def run_command(
        self,
        command: List[str],
        cwd: str,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        run_id: Optional[str] = None
    ) -> SandboxResult:
        """
        Executes a command safely inside `cwd` with strict timeout, memory limits,
        output caps, and recursive process tree termination.
        """
        effective_timeout = timeout or self.timeout_sec
        clean_env = os.environ.copy()
        clean_env["PYTHONDONTWRITEBYTECODE"] = "1"
        clean_env["PYTHONPATH"] = cwd + os.pathsep + clean_env.get("PYTHONPATH", "")

        # Security: Strip host secrets from sandbox environment
        sensitive_patterns = ("API_KEY", "SECRET", "PASSWORD", "TOKEN", "DATABASE_URL")
        for k in list(clean_env.keys()):
            if any(pat in k.upper() for pat in sensitive_patterns):
                del clean_env[k]

        if env_vars:
            clean_env.update(env_vars)

        start_time = time.perf_counter()
        timed_out = False
        memory_exceeded = False
        stdout_data = ""
        stderr_data = ""
        returncode = -1
        proc = None

        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=clean_env
            )

            if run_id:
                async with self._lock:
                    if run_id not in self._active_pids:
                        self._active_pids[run_id] = set()
                    self._active_pids[run_id].add(proc.pid)

            # Monitor memory and timeout in background
            async def memory_monitor():
                nonlocal memory_exceeded
                try:
                    p = psutil.Process(proc.pid)
                    while proc.returncode is None:
                        total_mem = p.memory_info().rss
                        for child in p.children(recursive=True):
                            try:
                                total_mem += child.memory_info().rss
                            except Exception:
                                pass
                        total_mb = total_mem / (1024 * 1024)
                        if total_mb > self.MAX_MEMORY_MB:
                            memory_exceeded = True
                            self._kill_process_tree(proc.pid)
                            break
                        await asyncio.sleep(0.2)
                except Exception:
                    pass

            monitor_task = asyncio.create_task(memory_monitor())

            try:
                out, err = await asyncio.wait_for(proc.communicate(), timeout=effective_timeout)
                stdout_data = out.decode("utf-8", errors="replace")
                stderr_data = err.decode("utf-8", errors="replace")
                returncode = proc.returncode if proc.returncode is not None else 0
            except asyncio.TimeoutError:
                timed_out = True
                self._kill_process_tree(proc.pid)
                try:
                    await asyncio.wait_for(proc.wait(), timeout=2.0)
                except Exception:
                    pass
                stderr_data = f"Execution timed out after {effective_timeout} seconds."
                returncode = 124
            finally:
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass

            if memory_exceeded:
                returncode = 137
                stderr_data = f"Execution aborted: Memory limit of {self.MAX_MEMORY_MB}MB exceeded."

            # Output size capping
            if len(stdout_data) > self.MAX_OUTPUT_BYTES:
                stdout_data = stdout_data[:self.MAX_OUTPUT_BYTES] + "\n... [Output truncated: exceeded 512KB limit]"
            if len(stderr_data) > self.MAX_OUTPUT_BYTES:
                stderr_data = stderr_data[:self.MAX_OUTPUT_BYTES] + "\n... [Stderr truncated: exceeded 512KB limit]"

        except Exception as ex:
            stderr_data = f"Process invocation error: {str(ex)}"
            returncode = 1
        finally:
            if run_id and proc:
                async with self._lock:
                    if run_id in self._active_pids and proc.pid in self._active_pids[run_id]:
                        self._active_pids[run_id].remove(proc.pid)

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return SandboxResult(
            returncode=returncode,
            stdout=stdout_data,
            stderr=stderr_data,
            duration_ms=duration_ms,
            timed_out=timed_out
        )

    def terminate_run_processes(self, run_id: str):
        """Kills all process trees associated with a run_id immediately."""
        pids = self._active_pids.get(run_id, set())
        for pid in list(pids):
            self._kill_process_tree(pid)
        if run_id in self._active_pids:
            del self._active_pids[run_id]

    def _kill_process_tree(self, pid: int):
        """Recursively terminates a process and all its children via psutil."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.kill()
                except Exception:
                    pass
            try:
                parent.kill()
            except Exception:
                pass
            psutil.wait_procs(children + [parent], timeout=2.0)
        except Exception:
            pass

    def create_isolated_workspace(self, source_dir: str) -> str:
        """Creates a temporary isolated directory copied from source_dir."""
        temp_dir = tempfile.mkdtemp(prefix="sentinel_sandbox_")
        if os.path.isdir(source_dir):
            for item in os.listdir(source_dir):
                if item in (".git", ".venv", "venv", "__pycache__", ".pytest_cache"):
                    continue
                s_path = os.path.join(source_dir, item)
                d_path = os.path.join(temp_dir, item)
                if os.path.isdir(s_path):
                    shutil.copytree(s_path, d_path, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                else:
                    shutil.copy2(s_path, d_path)
        return temp_dir

    def cleanup_workspace(self, temp_dir: str):
        """Safely cleans up temporary isolated workspace."""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


# Singleton runner instance
default_runner = SandboxRunner()
