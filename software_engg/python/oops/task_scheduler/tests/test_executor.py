"""
tests/test_executor.py — Unit tests for TaskExecutor.
"""
import asyncio
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scheduler.executor import TaskExecutor
from scheduler.models import Task, CronExpression, Priority, TaskStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(func, timeout=None, retry_count=0, name="test"):
    return Task(
        name        = name,
        cron        = CronExpression("* * * * * *"),
        func        = func,
        priority    = Priority.NORMAL,
        retry_count = retry_count,
        timeout     = timeout,
    )


# ---------------------------------------------------------------------------
# Sync callable
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sync_success():
    def greet():
        print("hello, world")

    executor = TaskExecutor()
    result   = await executor.execute(_make_task(greet))
    assert result.status == TaskStatus.SUCCESS
    assert "hello, world" in (result.output or "")


@pytest.mark.asyncio
async def test_sync_failure():
    def bad():
        raise ValueError("boom")

    executor = TaskExecutor()
    result   = await executor.execute(_make_task(bad))
    assert result.status == TaskStatus.FAILED
    assert "ValueError" in (result.error or "")


@pytest.mark.asyncio
async def test_sync_with_args():
    results = []

    def add(a, b):
        results.append(a + b)

    task = _make_task(add)
    task.args = (3, 4)

    executor = TaskExecutor()
    r = await executor.execute(task)
    assert r.status == TaskStatus.SUCCESS
    assert results == [7]


# ---------------------------------------------------------------------------
# Async callable
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_success():
    async def async_work():
        await asyncio.sleep(0.01)
        print("async done")

    executor = TaskExecutor()
    result   = await executor.execute(_make_task(async_work))
    assert result.status == TaskStatus.SUCCESS
    assert "async done" in (result.output or "")


@pytest.mark.asyncio
async def test_async_failure():
    async def async_bad():
        raise RuntimeError("async boom")

    executor = TaskExecutor()
    result   = await executor.execute(_make_task(async_bad))
    assert result.status == TaskStatus.FAILED
    assert "RuntimeError" in (result.error or "")


# ---------------------------------------------------------------------------
# Timeout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_timeout_enforced():
    async def slow():
        await asyncio.sleep(10)

    task     = _make_task(slow, timeout=0.1)
    executor = TaskExecutor()
    result   = await executor.execute(task)
    assert result.status == TaskStatus.FAILED
    assert "timed out" in (result.error or "").lower()


@pytest.mark.asyncio
async def test_no_timeout():
    async def fast():
        await asyncio.sleep(0.05)

    task     = _make_task(fast, timeout=5.0)
    executor = TaskExecutor()
    result   = await executor.execute(task)
    assert result.status == TaskStatus.SUCCESS


# ---------------------------------------------------------------------------
# Duration
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_duration_recorded():
    import time

    def slow_sync():
        time.sleep(0.1)

    executor = TaskExecutor()
    result   = await executor.execute(_make_task(slow_sync))
    assert result.duration_seconds is not None
    assert result.duration_seconds >= 0.05
