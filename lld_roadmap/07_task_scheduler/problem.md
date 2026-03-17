# ⏰ Task Scheduler (Cron) — Problem Statement

## Category: Task / Workflow Management
**Difficulty**: Hard | **Time**: 45 min | **Week**: 7

---

## Problem Statement

Design an in-memory task scheduler that supports:

1. **One-time tasks**: Execute a task at a specific future time
2. **Recurring tasks**: Execute at intervals (every N seconds/minutes/hours)
3. **Cron-like scheduling**: Support cron expressions
4. **Priority-based execution**: Higher priority tasks execute first
5. **Dependency management**: Task B runs only after Task A completes
6. **Thread pool**: Configurable number of worker threads
7. **Retry on failure**: Configurable retry count and backoff strategy
8. **Task lifecycle**: Pending → Running → Completed / Failed / Retrying

---

## Requirements Gathering (Practice Questions)

1. Max concurrent tasks?
2. What happens if a task fails? Retry? Dead letter queue?
3. Do tasks have dependencies (DAG)?
4. Should we support cancellation of scheduled tasks?
5. Do we need persistence (survive restarts)?
6. What's the time granularity (seconds, milliseconds)?
7. Do we need task groups/batches?

---

## Core Entities

| Entity | Responsibility |
|--------|---------------|
| `Task` | Unit of work with execution logic |
| `TaskScheduler` | Main orchestrator — schedules and manages tasks |
| `TaskQueue` | Priority queue of pending tasks |
| `ThreadPool` | Pool of worker threads for execution |
| `TaskStatus` | Enum: Pending, Running, Completed, Failed, Retrying |
| `Schedule` | When to run: one-time, interval, cron |
| `RetryPolicy` | How to retry: max retries, backoff strategy |
| `TaskResult` | Outcome of task execution |

---

## Key Design Decisions

### 1. Task Definition (Command Pattern)
```python
class Task(ABC):
    def __init__(self, task_id: str, priority: int = 0):
        self.task_id = task_id
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.dependencies: List[str] = []
        self.retry_policy: Optional[RetryPolicy] = None
        self.retry_count = 0
    
    @abstractmethod
    def execute(self) -> TaskResult:
        """The actual work to be done"""
        pass
    
    def __lt__(self, other):
        """For priority queue ordering"""
        return self.priority > other.priority  # Higher priority first
```

### 2. Schedule Types
```python
class Schedule(ABC):
    @abstractmethod
    def next_run_time(self, current_time: float) -> Optional[float]:
        pass

class OneTimeSchedule(Schedule):
    def __init__(self, run_at: float):
        self.run_at = run_at
    
    def next_run_time(self, current_time: float) -> Optional[float]:
        if current_time < self.run_at:
            return self.run_at
        return None  # Already executed

class IntervalSchedule(Schedule):
    def __init__(self, interval_seconds: float, start_at: Optional[float] = None):
        self.interval = interval_seconds
        self.start_at = start_at or time.time()
        self.last_run: Optional[float] = None
    
    def next_run_time(self, current_time: float) -> Optional[float]:
        if self.last_run is None:
            return max(self.start_at, current_time)
        return self.last_run + self.interval

class CronSchedule(Schedule):
    def __init__(self, cron_expression: str):
        """Parse cron: '*/5 * * * *' = every 5 minutes"""
        self.expression = cron_expression
    
    def next_run_time(self, current_time: float) -> Optional[float]:
        pass  # Parse cron and calculate next run
```

### 3. Retry with Backoff (Strategy Pattern)
```python
class BackoffStrategy(ABC):
    @abstractmethod
    def get_delay(self, retry_count: int) -> float:
        pass

class FixedBackoff(BackoffStrategy):
    def __init__(self, delay: float):
        self.delay = delay
    
    def get_delay(self, retry_count: int) -> float:
        return self.delay

class ExponentialBackoff(BackoffStrategy):
    def __init__(self, base_delay: float, max_delay: float):
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def get_delay(self, retry_count: int) -> float:
        delay = self.base_delay * (2 ** retry_count)
        return min(delay, self.max_delay)

@dataclass
class RetryPolicy:
    max_retries: int
    backoff: BackoffStrategy
```

### 4. Task Scheduler (Core)
```python
class TaskScheduler:
    def __init__(self, max_workers: int = 4):
        self._task_queue: List[ScheduledTask] = []  # min-heap by next_run_time
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()
        self._running = False
    
    def schedule(self, task: Task, schedule: Schedule):
        with self._lock:
            next_run = schedule.next_run_time(time.time())
            if next_run:
                scheduled = ScheduledTask(task, schedule, next_run)
                heapq.heappush(self._task_queue, scheduled)
                self._tasks[task.task_id] = task
    
    def start(self):
        self._running = True
        threading.Thread(target=self._run_loop, daemon=True).start()
    
    def _run_loop(self):
        while self._running:
            with self._lock:
                if not self._task_queue:
                    time.sleep(0.1)
                    continue
                
                next_task = self._task_queue[0]
                if time.time() >= next_task.next_run_time:
                    scheduled = heapq.heappop(self._task_queue)
                    
                    # Check dependencies
                    if self._dependencies_met(scheduled.task):
                        self._executor.submit(self._execute_task, scheduled)
                    else:
                        # Re-schedule with small delay
                        scheduled.next_run_time = time.time() + 1
                        heapq.heappush(self._task_queue, scheduled)
                else:
                    time.sleep(0.01)
    
    def _execute_task(self, scheduled: ScheduledTask):
        task = scheduled.task
        task.status = TaskStatus.RUNNING
        try:
            result = task.execute()
            task.status = TaskStatus.COMPLETED
            # If recurring, reschedule
            next_run = scheduled.schedule.next_run_time(time.time())
            if next_run:
                scheduled.next_run_time = next_run
                with self._lock:
                    heapq.heappush(self._task_queue, scheduled)
        except Exception as e:
            self._handle_failure(scheduled, e)
    
    def _handle_failure(self, scheduled: ScheduledTask, error: Exception):
        task = scheduled.task
        if (task.retry_policy and 
            task.retry_count < task.retry_policy.max_retries):
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            delay = task.retry_policy.backoff.get_delay(task.retry_count)
            scheduled.next_run_time = time.time() + delay
            with self._lock:
                heapq.heappush(self._task_queue, scheduled)
        else:
            task.status = TaskStatus.FAILED
    
    def cancel(self, task_id: str):
        with self._lock:
            self._tasks[task_id].status = TaskStatus.CANCELLED
```

### 5. Dependency Management (DAG)
```python
def _dependencies_met(self, task: Task) -> bool:
    for dep_id in task.dependencies:
        dep_task = self._tasks.get(dep_id)
        if dep_task is None or dep_task.status != TaskStatus.COMPLETED:
            return False
    return True
```

---

## Variations This Unlocks

| Variation | What Changes |
|-----------|-------------|
| **Elevator System** | Tasks = floor requests, priority = direction optimization (SCAN algorithm) |
| **Traffic Signal** | Tasks = signal changes, schedule = timed intervals, state machine for light colors |
| **Workflow Engine** | Tasks with complex DAG dependencies, conditional branching |
| **Job Queue (Celery-like)** | Distributed version with message broker, same core scheduler |

---

## Interview Checklist

- [ ] Clarified requirements (recurring, dependencies, retry)
- [ ] Designed Task with Command pattern
- [ ] Implemented Schedule types (one-time, interval, cron)
- [ ] Implemented priority queue with heap
- [ ] Implemented thread pool for concurrent execution
- [ ] Implemented retry with backoff strategies
- [ ] Implemented dependency checking (DAG)
- [ ] Discussed cancellation and task lifecycle
- [ ] Discussed persistence and crash recovery
