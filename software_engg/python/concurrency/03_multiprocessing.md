# Multiprocessing in Python

## Why Multiprocessing?

The GIL prevents threads from achieving true parallelism for CPU-bound work. **Multiprocessing** creates separate OS processes, each with its own Python interpreter and GIL.

```
Threading (GIL limited):              Multiprocessing (true parallelism):
  Process (1 GIL)                      Process 1 (GIL 1)    Process 2 (GIL 2)
  ┌─────────────────┐                  ┌─────────────┐     ┌─────────────┐
  │ Thread1 ██░░██  │                  │ Thread ████ │     │ Thread ████ │
  │ Thread2 ░░██░░  │                  │ (runs free) │     │ (runs free) │
  │ (sharing GIL)   │                  └─────────────┘     └─────────────┘
  └─────────────────┘                   Core 1               Core 2
     1 core used                        Real parallelism!
```

---

## Basic Process Creation

```python
import multiprocessing
import os

def worker(name):
    print(f"{name}: PID={os.getpid()}, Parent={os.getppid()}")
    # Heavy computation here...
    total = sum(range(50_000_000))
    print(f"{name}: done, total={total}")

if __name__ == "__main__":    # ← REQUIRED on Windows!
    p1 = multiprocessing.Process(target=worker, args=("Process-1",))
    p2 = multiprocessing.Process(target=worker, args=("Process-2",))
    
    p1.start()
    p2.start()
    
    p1.join()  # Wait for completion
    p2.join()
    
    print(f"Main: PID={os.getpid()}")
    print(f"p1 exit code: {p1.exitcode}")
```

> **⚠️ `if __name__ == "__main__":`** is mandatory on Windows. Without it, child processes re-import the module and try to spawn more processes → infinite fork bomb.

### Process Properties

```python
p = multiprocessing.Process(target=worker, args=("P1",))
p.daemon = True         # Killed when parent exits
p.name = "MyProcess"
p.start()

print(p.pid)            # OS process ID
print(p.is_alive())     # True if running
print(p.exitcode)       # None (still running), 0 (success), >0 (error)

p.terminate()           # Send SIGTERM
p.kill()                # Send SIGKILL (force)
p.join(timeout=5)       # Wait with timeout
```

---

## Inter-Process Communication (IPC)

Processes have **separate memory** — they can't share variables directly. Use IPC mechanisms.

### Queue (Thread & Process Safe)

```python
from multiprocessing import Process, Queue

def producer(q):
    for i in range(5):
        q.put(f"item-{i}")
    q.put(None)  # Sentinel to signal done

def consumer(q):
    while True:
        item = q.get()  # Blocks until item available
        if item is None:
            break
        print(f"Consumed: {item}")

if __name__ == "__main__":
    q = Queue()
    p1 = Process(target=producer, args=(q,))
    p2 = Process(target=consumer, args=(q,))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

### Pipe (Two-Way Communication)

```python
from multiprocessing import Process, Pipe

def sender(conn):
    conn.send("Hello from sender!")
    conn.send([1, 2, 3])
    response = conn.recv()
    print(f"Sender got: {response}")
    conn.close()

def receiver(conn):
    msg = conn.recv()
    print(f"Receiver got: {msg}")
    data = conn.recv()
    print(f"Receiver got: {data}")
    conn.send("ACK")
    conn.close()

if __name__ == "__main__":
    parent_conn, child_conn = Pipe()  # Two endpoints
    p1 = Process(target=sender, args=(parent_conn,))
    p2 = Process(target=receiver, args=(child_conn,))
    p1.start(); p2.start()
    p1.join(); p2.join()
```

| IPC Method | Direction | Multiple Producers/Consumers | Use Case |
|-----------|-----------|------------------------------|----------|
| **Queue** | Multi-directional | ✅ Yes | Task distribution, results collection |
| **Pipe** | Bi-directional (but 2 endpoints) | ❌ No (2 endpoints only) | Parent-child communication |

---

## Shared Memory

### Value and Array

```python
from multiprocessing import Process, Value, Array

def increment(shared_counter, shared_array, lock):
    for i in range(100_000):
        with lock:
            shared_counter.value += 1
    
    for i in range(len(shared_array)):
        with lock:
            shared_array[i] += 1

if __name__ == "__main__":
    counter = Value('i', 0)       # 'i' = integer, initialized to 0
    arr = Array('d', [0.0, 0.0, 0.0])  # 'd' = double float
    lock = multiprocessing.Lock()
    
    processes = [Process(target=increment, args=(counter, arr, lock)) for _ in range(4)]
    for p in processes: p.start()
    for p in processes: p.join()
    
    print(f"Counter: {counter.value}")    # 400,000
    print(f"Array: {list(arr)}")          # [4.0, 4.0, 4.0]
```

### Manager (Shared Complex Objects)

```python
from multiprocessing import Process, Manager

def worker(shared_dict, shared_list, name):
    shared_dict[name] = f"Hello from {name}"
    shared_list.append(name)

if __name__ == "__main__":
    with Manager() as manager:
        d = manager.dict()    # Shared dictionary
        l = manager.list()    # Shared list
        
        processes = []
        for name in ["A", "B", "C"]:
            p = Process(target=worker, args=(d, l, name))
            p.start()
            processes.append(p)
        
        for p in processes: p.join()
        
        print(dict(d))   # {'A': 'Hello from A', 'B': ...}
        print(list(l))   # ['A', 'B', 'C']
```

> **Manager** uses a server process + proxies. Slower than `Value`/`Array` but supports complex types (dict, list, Namespace).

---

## Process Pool

### Pool (Legacy API)

```python
from multiprocessing import Pool
import time

def process_item(item):
    time.sleep(0.5)  # Simulate work
    return item ** 2

if __name__ == "__main__":
    with Pool(processes=4) as pool:
        # map — ordered results (like built-in map)
        results = pool.map(process_item, range(20))
        print(results)  # [0, 1, 4, 9, 16, ...]

        # imap — lazy iterator (memory efficient for large input)
        for result in pool.imap(process_item, range(20)):
            print(result)

        # imap_unordered — results as they complete (fastest)
        for result in pool.imap_unordered(process_item, range(20)):
            print(result)

        # apply_async — single task, non-blocking
        future = pool.apply_async(process_item, (42,))
        print(future.get(timeout=10))  # 1764

        # starmap — multiple arguments
        pairs = [(1, 2), (3, 4), (5, 6)]
        results = pool.starmap(lambda a, b: a + b, pairs)
```

### ProcessPoolExecutor (Modern API)

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import math

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    return True

def find_primes(start, end):
    return [n for n in range(start, end) if is_prime(n)]

if __name__ == "__main__":
    # Split range into chunks
    ranges = [(i, i + 1_000_000) for i in range(0, 10_000_000, 1_000_000)]
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(find_primes, s, e) for s, e in ranges]
        
        all_primes = []
        for future in as_completed(futures):
            all_primes.extend(future.result())
    
    print(f"Found {len(all_primes)} primes")
```

### Pool vs ProcessPoolExecutor

| Feature | `Pool` | `ProcessPoolExecutor` |
|---------|--------|----------------------|
| API | Legacy (multiprocessing) | Modern (concurrent.futures) |
| `map` | `pool.map()`, `imap()` | `executor.map()` |
| Single task | `apply_async()` | `executor.submit()` → `Future` |
| Error handling | Callbacks | `Future.result()` raises |
| Cancel | ❌ | `future.cancel()` |
| Mix threads/processes | ❌ | ✅ Same API for both |

---

## Start Methods

How child processes are created.

| Method | OS | How | Pros | Cons |
|--------|-----|-----|------|------|
| **fork** | Linux/macOS | Copy parent process (COW) | Fast, inherits state | Unsafe with threads |
| **spawn** | All (default on Windows) | New interpreter, import module | Safe, clean | Slower, must be picklable |
| **forkserver** | Linux/macOS | Fork from a server process | Safe + faster than spawn | Extra server process |

```python
import multiprocessing

# Set start method (call ONCE at program start)
multiprocessing.set_start_method('spawn')

# Or per-context
ctx = multiprocessing.get_context('fork')
p = ctx.Process(target=worker)
```

---

## Pickling Requirement

With `spawn` (and `forkserver`), all arguments and functions must be **picklable** (serializable).

```python
# ✅ Picklable: top-level functions, classes, basic types
def worker(x):
    return x * 2

# ❌ NOT picklable: lambda, local function, closure
bad = lambda x: x * 2         # Can't pickle lambda
def outer():
    def inner(x): return x * 2  # Can't pickle local function
    return inner
```

---

## Interview Questions — Multiprocessing

### Q1: When to use threading vs multiprocessing?

| Scenario | Use |
|----------|-----|
| I/O-bound (HTTP, DB, files) | `threading` or `asyncio` |
| CPU-bound (math, image processing) | `multiprocessing` |
| Need shared memory (simple) | `threading` (direct access) |
| Need isolation (crash safety) | `multiprocessing` |

### Q2: How do processes communicate?

Since processes have separate memory:
1. **Queue** — thread/process-safe FIFO (most common)
2. **Pipe** — two-endpoint channel (parent-child)
3. **Shared Memory** — `Value`, `Array` (fast, needs lock)
4. **Manager** — proxy objects for complex types (slower)

### Q3: What is the `if __name__ == "__main__"` guard and why is it needed?

On Windows (and `spawn` start method), child processes **re-import** the module. Without the guard, the module-level process creation code runs again in the child → infinite process spawning. The guard ensures process creation only happens in the main process.
