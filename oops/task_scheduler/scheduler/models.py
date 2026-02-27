"""
models.py — Core data models for the Task Scheduler.
"""
from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Deque, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Priority(Enum):
    """Task execution priority — lower value = higher urgency."""
    CRITICAL = 1
    HIGH     = 2
    NORMAL   = 3
    LOW      = 4

    def __lt__(self, other: "Priority") -> bool:
        return self.value < other.value


class TaskStatus(Enum):
    """Lifecycle state of a task."""
    PENDING   = "PENDING"
    RUNNING   = "RUNNING"
    SUCCESS   = "SUCCESS"
    FAILED    = "FAILED"
    PAUSED    = "PAUSED"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CronExpression:
    """Immutable wrapper around a cron string.  Validated on construction."""
    expression: str

    def __post_init__(self) -> None:
        # lazy import to avoid circular dependency
        from .cron_parser import CronParser
        CronParser.validate(self.expression)

    def __str__(self) -> str:
        return self.expression


# ---------------------------------------------------------------------------
# Task Result
# ---------------------------------------------------------------------------

@dataclass
class TaskResult:
    """Outcome of a single execution attempt."""
    task_id   : str
    task_name : str
    started_at: datetime
    ended_at  : Optional[datetime] = None
    status    : TaskStatus         = TaskStatus.RUNNING
    output    : Optional[str]      = None
    error     : Optional[str]      = None
    attempt   : int                = 1

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id"   : self.task_id,
            "task_name" : self.task_name,
            "started_at": self.started_at.isoformat(),
            "ended_at"  : self.ended_at.isoformat() if self.ended_at else None,
            "status"    : self.status.value,
            "output"    : self.output,
            "error"     : self.error,
            "attempt"   : self.attempt,
        }


# ---------------------------------------------------------------------------
# Execution History
# ---------------------------------------------------------------------------

@dataclass
class ExecutionHistory:
    """Ring-buffer of the last *maxlen* TaskResults for a single task."""
    task_id: str
    maxlen : int = 50
    results: Deque[TaskResult] = field(default_factory=lambda: deque(maxlen=50))

    def add(self, result: TaskResult) -> None:
        self.results.append(result)

    @property
    def last(self) -> Optional[TaskResult]:
        return self.results[-1] if self.results else None

    def as_list(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.results]


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Full descriptor for a schedulable unit of work."""
    name       : str
    cron       : CronExpression
    func       : Callable[..., Any]
    args       : tuple                = field(default_factory=tuple)
    kwargs     : Dict[str, Any]       = field(default_factory=dict)
    priority   : Priority             = Priority.NORMAL
    retry_count: int                  = 0          # extra attempts after first failure
    timeout    : Optional[float]      = None       # seconds; None = no limit
    tags       : List[str]            = field(default_factory=list)
    enabled    : bool                 = True
    id         : str                  = field(default_factory=lambda: str(uuid.uuid4()))
    created_at : datetime             = field(default_factory=datetime.utcnow)
    status     : TaskStatus           = TaskStatus.PENDING

    # runtime — populated by the scheduler
    next_run   : Optional[datetime]   = field(default=None, repr=False)
    last_run   : Optional[datetime]   = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id"         : self.id,
            "name"       : self.name,
            "cron"       : str(self.cron),
            "priority"   : self.priority.name,
            "retry_count": self.retry_count,
            "timeout"    : self.timeout,
            "tags"       : self.tags,
            "enabled"    : self.enabled,
            "status"     : self.status.value,
            "created_at" : self.created_at.isoformat(),
            "next_run"   : self.next_run.isoformat() if self.next_run else None,
            "last_run"   : self.last_run.isoformat() if self.last_run else None,
        }
