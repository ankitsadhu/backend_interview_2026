"""
scheduler.py — TaskScheduler: the core scheduling engine.

Architecture
------------
* Maintains an asyncio.PriorityQueue of (next_run_timestamp, priority_value, task_id).
* A single async _tick_loop() wakes up frequently (every 0.25 s) and fires
  any tasks whose next_run <= now.
* Tasks are executed via TaskExecutor in the same event loop.
* Failed tasks are retried up to task.retry_count times before being marked FAILED.
* After each run the task is re-enqueued with a new next_run computed from the
  cron expression.
* Thread-safe: external callers can add/remove tasks from any thread using
  asyncio.run_coroutine_threadsafe.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional

from .cron_parser import CronParser
from .executor import TaskExecutor
from .models import Priority, Task, TaskResult, TaskStatus
from .store import TaskStore

logger = logging.getLogger("task_scheduler")


class TaskScheduler:
    """
    High-level scheduler.

    Usage
    -----
    >>> scheduler = TaskScheduler()
    >>> scheduler.add_task(task)
    >>> asyncio.run(scheduler.start())   # blocks until stopped
    """

    TICK_INTERVAL = 0.25  # seconds between queue checks

    def __init__(
        self,
        persist_path: Optional[str] = None,
        on_result: Optional[Callable[[TaskResult], None]] = None,
    ) -> None:
        self._store     = TaskStore(persist_path)
        self._executor  = TaskExecutor()
        self._on_result = on_result        # optional callback after each execution
        self._running   = False
        self._queue     : asyncio.PriorityQueue  = asyncio.PriorityQueue()
        self._lock      : Optional[asyncio.Lock] = None
        # Track tasks currently being executed to avoid double-fire
        self._in_flight : Dict[str, int] = {}  # task_id -> attempt number

    # ------------------------------------------------------------------
    # Public API — safe to call from any thread/coroutine
    # ------------------------------------------------------------------

    def add_task(self, task: Task) -> str:
        """Register a task. Returns the task id."""
        self._store.add(task)
        next_run = CronParser.get_next_run(str(task.cron), datetime.utcnow())
        self._store.set_next_run(task.id, next_run)
        task.next_run = next_run
        logger.info("Registered task '%s' [%s] next_run=%s", task.name, task.id[:8], next_run)
        if self._running:
            self._enqueue(task, next_run)
        return task.id

    def remove_task(self, task_id: str) -> bool:
        """Remove a task. Returns True if it existed."""
        removed = self._store.remove(task_id)
        if removed:
            logger.info("Removed task %s", task_id[:8])
        return removed

    def pause_task(self, task_id: str) -> bool:
        """Pause a task (it stays registered but won't fire)."""
        task = self._store.get(task_id)
        if task:
            task.enabled = False
            self._store.set_status(task_id, TaskStatus.PAUSED)
            logger.info("Paused task '%s'", task.name)
            return True
        return False

    def resume_task(self, task_id: str) -> bool:
        """Resume a previously paused task."""
        task = self._store.get(task_id)
        if task:
            task.enabled = True
            self._store.set_status(task_id, TaskStatus.PENDING)
            next_run = CronParser.get_next_run(str(task.cron), datetime.utcnow())
            self._store.set_next_run(task_id, next_run)
            task.next_run = next_run
            if self._running:
                self._enqueue(task, next_run)
            logger.info("Resumed task '%s'", task.name)
            return True
        return False

    def list_tasks(self) -> List[Task]:
        return self._store.all_tasks()

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._store.get(task_id)

    def get_history(self, task_id: str) -> List[dict]:
        return self._store.get_history(task_id)

    async def run_now(self, task_id: str) -> Optional[TaskResult]:
        """Immediately execute a task once (one-shot), bypassing the schedule."""
        task = self._store.get(task_id)
        if not task:
            return None
        return await self._fire(task, attempt=1)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the scheduler loop (blocks until stop() is called)."""
        self._running = True
        self._lock    = asyncio.Lock()
        self._queue   = asyncio.PriorityQueue()

        # Seed the queue with all registered tasks
        for task in self._store.enabled_tasks():
            if task.next_run:
                self._enqueue(task, task.next_run)

        logger.info("TaskScheduler started — %d tasks loaded", len(self._store.enabled_tasks()))

        try:
            await self._tick_loop()
        finally:
            self._running = False
            logger.info("TaskScheduler stopped")

    def stop(self) -> None:
        """Signal the scheduler to stop after the current tick."""
        self._running = False

    # ------------------------------------------------------------------
    # Internal scheduling loop
    # ------------------------------------------------------------------

    async def _tick_loop(self) -> None:
        while self._running:
            now = datetime.utcnow()
            fired: List[tuple] = []

            # Drain all due items from the priority queue
            while not self._queue.empty():
                ts, priority_val, task_id = await self._queue.get()
                run_at = datetime.utcfromtimestamp(ts)
                if run_at <= now:
                    fired.append((ts, priority_val, task_id))
                else:
                    # Put it back — not yet due
                    await self._queue.put((ts, priority_val, task_id))
                    break

            # Fire due tasks (sorted by priority value, then time)
            fired.sort(key=lambda x: (x[1], x[0]))
            for _, _, task_id in fired:
                task = self._store.get(task_id)
                if task and task.enabled:
                    asyncio.create_task(self._execute_with_retry(task))

            await asyncio.sleep(self.TICK_INTERVAL)

    async def _execute_with_retry(self, task: Task) -> None:
        """Execute a task, retrying up to task.retry_count times on failure."""
        self._store.set_status(task.id, TaskStatus.RUNNING)
        self._store.set_last_run(task.id, datetime.utcnow())
        task.last_run = datetime.utcnow()

        result = None
        for attempt in range(1, task.retry_count + 2):  # +2 for initial attempt
            result = await self._fire(task, attempt)
            self._store.record_result(result)
            if result.status == TaskStatus.SUCCESS:
                break
            if attempt <= task.retry_count:
                logger.warning(
                    "Task '%s' failed (attempt %d/%d), retrying...",
                    task.name, attempt, task.retry_count + 1,
                )
                await asyncio.sleep(min(2 ** attempt, 30))  # exponential back-off

        if result:
            self._store.set_status(task.id, result.status)
            if self._on_result:
                self._on_result(result)

        # Re-schedule for next cron time
        try:
            next_run = CronParser.get_next_run(str(task.cron), datetime.utcnow())
            self._store.set_next_run(task.id, next_run)
            task.next_run = next_run
            self._store.set_status(task.id, TaskStatus.PENDING)
            self._enqueue(task, next_run)
        except Exception as exc:
            logger.error("Failed to reschedule task '%s': %s", task.name, exc)

    async def _fire(self, task: Task, attempt: int) -> TaskResult:
        logger.debug("Firing task '%s' (attempt %d)", task.name, attempt)
        result = await self._executor.execute(task, attempt=attempt)
        log_fn = logger.info if result.status == TaskStatus.SUCCESS else logger.error
        log_fn(
            "Task '%s' [%s] — %s (%.3fs)",
            task.name, task.id[:8], result.status.value,
            result.duration_seconds or 0,
        )
        return result

    # ------------------------------------------------------------------
    # Queue helpers
    # ------------------------------------------------------------------

    def _enqueue(self, task: Task, run_at: datetime) -> None:
        ts = run_at.timestamp()
        self._queue.put_nowait((ts, task.priority.value, task.id))
