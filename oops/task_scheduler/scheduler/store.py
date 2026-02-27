"""
store.py — In-memory task store with optional JSON persistence.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from .models import ExecutionHistory, Task, TaskResult, TaskStatus


class TaskStore:
    """
    Manages the collection of Task objects and their execution histories.
    Optionally persists task metadata to a JSON file on disk.
    """

    def __init__(self, persist_path: Optional[str] = None) -> None:
        self._tasks    : Dict[str, Task]             = {}
        self._histories: Dict[str, ExecutionHistory] = {}
        self._persist  = persist_path
        if persist_path and os.path.exists(persist_path):
            self._load(persist_path)

    # ------------------------------------------------------------------
    # Task CRUD
    # ------------------------------------------------------------------

    def add(self, task: Task) -> None:
        self._tasks[task.id]     = task
        self._histories[task.id] = ExecutionHistory(task_id=task.id)
        self._save()

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def remove(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            del self._histories[task_id]
            self._save()
            return True
        return False

    def all_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def enabled_tasks(self) -> List[Task]:
        return [t for t in self._tasks.values() if t.enabled]

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    def set_status(self, task_id: str, status: TaskStatus) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].status = status
            self._save()

    def set_next_run(self, task_id: str, dt: datetime) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].next_run = dt

    def set_last_run(self, task_id: str, dt: datetime) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].last_run = dt

    # ------------------------------------------------------------------
    # Execution history
    # ------------------------------------------------------------------

    def record_result(self, result: TaskResult) -> None:
        history = self._histories.get(result.task_id)
        if history:
            history.add(result)

    def get_history(self, task_id: str) -> List[dict]:
        h = self._histories.get(task_id)
        return h.as_list() if h else []

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save(self) -> None:
        if not self._persist:
            return
        data = {tid: t.to_dict() for tid, t in self._tasks.items()}
        with open(self._persist, "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2)

    def _load(self, path: str) -> None:
        """
        Load task metadata from JSON.  Since callables can't be serialised,
        only the metadata is stored; the callable must be re-registered at
        runtime.  This is intentional — it mirrors production schedulers.
        """
        try:
            with open(path, encoding="utf-8") as fp:
                _ = json.load(fp)
            # Full reconstruction requires the caller to re-register callables.
            # We just validate the file is readable JSON here.
        except (json.JSONDecodeError, OSError):
            pass  # corrupt file — start fresh
