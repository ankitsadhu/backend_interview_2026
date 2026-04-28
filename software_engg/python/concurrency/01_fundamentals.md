# Concurrency Fundamentals

## Concurrency vs Parallelism

```
CONCURRENCY:                           PARALLELISM:
  Multiple tasks make progress           Multiple tasks execute simultaneously
  (may alternate on 1 CPU)               (requires multiple CPUs)

  Single core:                           Multi core:
  ┌──┬──┬──┬──┬──┬──┬──┬──┐            ┌──────────────────┐
  │T1│T2│T1│T2│T1│T2│T1│T2│            │ Core1: T1 T1 T1  │
  └──┴──┴──┴──┴──┴──┴──┴──┘            │ Core2: T2 T2 T2  │
      Interleaved (concurrent)           └──────────────────┘
                                             Simultaneous (parallel)

  Concurrency = STRUCTURE (dealing with lots of things at once)
  Parallelism = EXECUTION (doing lots of things at once)
  
  You can have concurrency without parallelism (single core, time-slicing)
  Parallelism implies concurrency
```

---

## Processes vs Threads

```
PROCESS:                                THREAD:
┌──────────────────────────┐           ┌──────────────────────────┐
│ Process A                │           │ Process A                │
│ ┌──────────────────────┐ │           │ ┌───────┐ ┌───────┐     │
│ │  Own Memory Space    │ │           │ │Thread1│ │Thread2│     │
│ │  Own File Descriptors│ │           │ │ Own   │ │ Own   │     │
│ │  Own PID             │ │           │ │ Stack │ │ Stack │     │
│ │  Own Registers       │ │           │ └───┬───┘ └───┬───┘     │
│ └──────────────────────┘ │           │     │         │          │
│                          │           │  ┌──┴─────────┴──┐      │
│ Process B                │           │  │ Shared Memory  │      │
│ ┌──────────────────────┐ │           │  │ Shared Heap    │      │
│ │  Own Memory Space    │ │           │  │ Shared FDs     │      │
│ │  (isolated from A)   │ │           │  │ Shared Code    │      │
│ └──────────────────────┘ │           │  └────────────────┘      │
└──────────────────────────┘           └──────────────────────────┘
```

| Aspect | Process | Thread |
|--------|---------|--------|
| **Memory** | Separate address space | Shared address space |
| **Creation cost** | Heavy (~10-100ms) | Light (~0.1-1ms) |
| **Communication** | IPC (pipes, queues, shared memory) | Direct memory access |
| **Isolation** | Strong (crash doesn't affect others) | Weak (one bad thread can crash all) |
| **Context switch** | Expensive (save/restore full state) | Cheaper (save/restore thread state) |
| **GIL (Python)** | Each process has own GIL ✅ | All threads share one GIL ❌ |
| **Use case** | CPU-bound work, isolation | I/O-bound work, shared state |

---

## CPU-Bound vs I/O-Bound

```
CPU-BOUND:                              I/O-BOUND:
  Task spends time computing              Task spends time waiting
  
  CPU ████████████████████               CPU ██░░░░██░░░░██░░░░
                                              ↑wait  ↑wait  ↑wait
  
  Examples:                              Examples:
  - Image processing                     - HTTP requests
  - Video encoding                       - Database queries
  - ML training                          - File reading
  - Compression                          - API calls
  - Math computation                     - WebSocket connections
  
  Solution: Parallelism                  Solution: Concurrency
  (multiple CPUs)                        (overlap waiting)
  Python: multiprocessing                Python: threading or asyncio
```

| Workload | Best Python Approach | Why |
|----------|---------------------|-----|
| **I/O-bound** | `asyncio` or `threading` | GIL released during I/O waits |
| **CPU-bound** | `multiprocessing` | Bypasses GIL (separate processes) |
| **Mixed** | `asyncio` + `ProcessPoolExecutor` | Async for I/O, processes for CPU |

---

## The GIL (Global Interpreter Lock)

The **Global Interpreter Lock** is a mutex in CPython that allows only **one thread to execute Python bytecode at a time**.

```
WITH GIL (CPython):
  Thread 1: ██░░██░░██░░      (acquires GIL, releases, acquires...)
  Thread 2: ░░██░░██░░██      (waits for GIL, acquires, releases...)
  
  Even on 4 cores, only 1 thread runs Python at a time!

WHY does the GIL exist?
  1. Simplifies CPython's memory management (reference counting)
  2. Makes C extensions easier to write (no thread-safety needed)
  3. Single-threaded performance is faster with GIL

WHEN is the GIL released?
  1. During I/O operations (file read, network, sleep)
  2. During C extension calls (NumPy, PIL, etc.)
  3. Every N bytecode instructions (thread switching)
```

### GIL Impact Demo

```python
import threading
import time

def cpu_task():
    """CPU-bound: count to 100 million"""
    total = 0
    for i in range(100_000_000):
        total += 1

# Single-threaded
start = time.time()
cpu_task()
cpu_task()
print(f"Sequential: {time.time() - start:.2f}s")  # ~8s

# Multi-threaded (NO speedup due to GIL!)
start = time.time()
t1 = threading.Thread(target=cpu_task)
t2 = threading.Thread(target=cpu_task)
t1.start(); t2.start()
t1.join(); t2.join()
print(f"Threaded: {time.time() - start:.2f}s")     # ~8s (same or SLOWER!)
```

```python
import multiprocessing
import time

def cpu_task():
    total = 0
    for i in range(100_000_000):
        total += 1

# Multi-process (actual speedup!)
start = time.time()
p1 = multiprocessing.Process(target=cpu_task)
p2 = multiprocessing.Process(target=cpu_task)
p1.start(); p2.start()
p1.join(); p2.join()
print(f"Multiprocess: {time.time() - start:.2f}s")  # ~4s (2x speedup!)
```

### Free-Threaded Python (PEP 703 — Python 3.13+)

```
Python 3.13 introduces EXPERIMENTAL no-GIL mode:
  python3.13t  (t = free-threaded build)

  - Per-object locks instead of global lock
  - True parallelism for multi-threaded Python code
  - Some single-threaded performance penalty (~5-10%)
  - C extensions need updates for thread safety
  - Still experimental, not default yet
```

---

## Race Conditions

A **race condition** occurs when multiple threads/processes access shared data concurrently, and the result depends on the **timing** of execution.

```python
# RACE CONDITION EXAMPLE
import threading

counter = 0

def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1  # NOT atomic!
        # Actually 3 operations:
        #   1. READ counter   (temp = counter)
        #   2. INCREMENT       (temp = temp + 1)
        #   3. WRITE counter   (counter = temp)

t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)
t1.start(); t2.start()
t1.join(); t2.join()

print(counter)  # Expected: 2,000,000
                # Actual: ~1,500,000 (varies!) — RACE CONDITION!
```

```
The race:
  Thread 1: READ counter = 100
  Thread 2: READ counter = 100    ← reads SAME value!
  Thread 1: WRITE counter = 101
  Thread 2: WRITE counter = 101   ← overwrites Thread 1's write!
  
  Two increments → only +1 instead of +2!
```

### Fix: Use a Lock

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(1_000_000):
        with lock:              # Only one thread at a time
            counter += 1

t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)
t1.start(); t2.start()
t1.join(); t2.join()

print(counter)  # Always 2,000,000 ✅
```

---

## Deadlocks

A **deadlock** occurs when two or more threads are waiting for each other to release resources, creating a circular dependency.

```
Thread 1:                    Thread 2:
  acquire(lock_A) ✓           acquire(lock_B) ✓
  acquire(lock_B) → WAIT      acquire(lock_A) → WAIT
  
  Both waiting forever! → DEADLOCK
```

### Four Conditions for Deadlock (ALL required)

| Condition | Description |
|-----------|-------------|
| **Mutual Exclusion** | Resources can't be shared simultaneously |
| **Hold and Wait** | Thread holds one resource while waiting for another |
| **No Preemption** | Resources can't be forcibly taken away |
| **Circular Wait** | Circular chain of waiting threads |

### Deadlock Example

```python
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()

def task_1():
    with lock_a:
        print("Task 1: acquired lock_a")
        import time; time.sleep(0.1)  # Simulate work
        with lock_b:                   # WAITING for lock_b (held by task_2)
            print("Task 1: acquired lock_b")

def task_2():
    with lock_b:
        print("Task 2: acquired lock_b")
        import time; time.sleep(0.1)
        with lock_a:                   # WAITING for lock_a (held by task_1)
            print("Task 2: acquired lock_a")

# DEADLOCK! Both threads wait forever.
t1 = threading.Thread(target=task_1)
t2 = threading.Thread(target=task_2)
t1.start(); t2.start()
```

### Prevention Strategies

| Strategy | How | Example |
|----------|-----|---------|
| **Lock ordering** | Always acquire locks in the same global order | Always A before B |
| **Lock timeout** | Give up after a timeout | `lock.acquire(timeout=5)` |
| **Try-lock** | Non-blocking attempt | `if lock.acquire(blocking=False):` |
| **Single lock** | Use one lock for all shared resources | Simpler but less concurrent |
| **Lock-free** | Use atomic operations instead of locks | `queue.Queue`, atomic counters |

```python
# FIX: Lock ordering (both acquire A before B)
def task_1():
    with lock_a:
        with lock_b:
            print("Task 1: both locks")

def task_2():
    with lock_a:        # Same order as task_1!
        with lock_b:
            print("Task 2: both locks")
```

---

## Starvation and Livelock

### Starvation

A thread **never** gets access to a resource because other threads keep taking it.

```
Thread A (high priority): ██████████████████████████████
Thread B (low priority):  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ← STARVED!

Thread A keeps acquiring the lock before B can.
```

### Livelock

Threads are **not blocked** but keep responding to each other without making progress.

```
Analogy: Two people in a hallway, both step aside in the same direction,
         then both step back, then step aside again... forever.

Thread A: "B has the lock, I'll back off" → release → try again
Thread B: "A has the lock, I'll back off" → release → try again
→ Both keep yielding, neither makes progress!
```

---

## Thread Safety

A function/class is **thread-safe** if it can be safely called from multiple threads simultaneously.

### Thread-Safe in Python

| Data Structure | Thread-Safe? | Notes |
|---------------|-------------|-------|
| `list.append()` | ✅ (GIL) | Single operation is atomic due to GIL |
| `dict[key] = val` | ✅ (GIL) | Single operation atomic |
| `counter += 1` | ❌ | Three operations: read, increment, write |
| `queue.Queue` | ✅ | Designed for thread-safe FIFO |
| `collections.deque` | ✅ | For append/popleft (atomic under GIL) |
| `logging` | ✅ | Thread-safe by design |

> **Warning:** GIL makes *single bytecode operations* atomic, but compound operations (read-modify-write) are NOT atomic. Always use locks for compound operations.

---

## Interview Questions — Fundamentals

### Q1: What is the difference between concurrency and parallelism?

**Concurrency** = dealing with multiple things at once (structure). Multiple tasks can make progress, potentially on a single core via time-slicing.

**Parallelism** = doing multiple things at once (execution). Tasks literally run simultaneously on different CPU cores.

Analogy: A chef (1 person) handling multiple dishes by switching between them = concurrency. Multiple chefs each working on their own dish simultaneously = parallelism.

---

### Q2: What is the GIL and how do you work around it?

The **GIL** is a mutex in CPython allowing only one thread to execute Python bytecode at a time. It prevents true multi-threaded parallelism for CPU-bound work.

**Workarounds:**
1. `multiprocessing` — separate processes, each with own GIL
2. `asyncio` — for I/O-bound work (GIL released during I/O)
3. C extensions (NumPy) — release GIL during computation
4. `concurrent.futures.ProcessPoolExecutor` — easy process-based parallelism
5. Free-threaded Python 3.13+ (experimental)

---

### Q3: What causes a deadlock? How do you prevent it?

**Four conditions** (all required): mutual exclusion, hold-and-wait, no preemption, circular wait.

**Prevention:** Break any one condition:
- **Lock ordering** — always acquire locks in a consistent global order (breaks circular wait)
- **Timeouts** — `lock.acquire(timeout=5)` (breaks hold-and-wait)
- **Single lock** — use one coarse lock (breaks circular wait)
