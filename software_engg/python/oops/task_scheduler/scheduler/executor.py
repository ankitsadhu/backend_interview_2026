"""
executor.py — Task execution engine.

Handles:
  - Sync callables (run in thread pool so they don't block the event loop)
  - Async callables (awaited directly)
  - Per-task timeouts via asyncio.wait_for
  - Stdout/stderr capture using contextlib.redirect_stdout
  - Returns a TaskResult on every execution
"""
from __future__ import annotations

import asyncio
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from typing import Callable, Any

from .models import Task, TaskResult, TaskStatus


class TaskExecutor:
    """Execute a Task and return a TaskResult."""

    def __init__(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        self._loop = loop or asyncio.get_event_loop()

    async def execute(self, task: Task, attempt: int = 1) -> TaskResult:
        """Run *task* once and return a TaskResult."""
        started_at = datetime.utcnow()
        result = TaskResult(
            task_id   = task.id,
            task_name = task.name,
            started_at= started_at,
            attempt   = attempt,
        )
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        try:
            coro = self._call(task.func, task.args, task.kwargs, stdout_buf, stderr_buf)
            if task.timeout:
                output = await asyncio.wait_for(coro, timeout=task.timeout)
            else:
                output = await coro

            result.status  = TaskStatus.SUCCESS
            result.output  = stdout_buf.getvalue() or (str(output) if output is not None else None)

        except asyncio.TimeoutError:
            result.status = TaskStatus.FAILED
            result.error  = f"Task timed out after {task.timeout}s"

        except Exception:
            result.status = TaskStatus.FAILED
            result.error  = traceback.format_exc()
            captured_err  = stderr_buf.getvalue()
            if captured_err:
                result.error = captured_err + "\n" + result.error

        finally:
            result.ended_at = datetime.utcnow()

        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    async def _call(
        func: Callable[..., Any],
        args: tuple,
        kwargs: dict,
        stdout_buf: io.StringIO,
        stderr_buf: io.StringIO,
    ) -> Any:
        """Invoke *func* with I/O capture, bridging sync/async."""
        if asyncio.iscoroutinefunction(func):
            with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                return await func(*args, **kwargs)
        else:
            # Run sync function in the default thread executor
            loop = asyncio.get_event_loop()

            def _run():
                with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                    return func(*args, **kwargs)

            return await loop.run_in_executor(None, _run)
