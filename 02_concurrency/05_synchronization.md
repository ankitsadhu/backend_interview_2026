# Synchronization Deep Dive

## Why Synchronization?

When multiple threads/processes access shared data, **synchronization** ensures correctness by controlling access.

```
WITHOUT synchronization:         WITH synchronization:
  Thread A: read(x=0)             Thread A: acquire(lock)
  Thread B: read(x=0)                        read(x=0)
  Thread A: write(x=1)                       write(x=1)
  Thread B: write(x=1)                       release(lock)
  Result: x=1 (lost update!)     Thread B: acquire(lock)
                                             read(x=1)
                                             write(x=2)
                                             release(lock)
                                  Result: x=2 ✅
```

---

## Mutex (Mutual Exclusion)

The simplest synchronization primitive. Only one thread can hold it at a time.

```python
import threading

mutex = threading.Lock()

# Only one thread enters at a time
def critical_section():
    with mutex:
        # Read shared state
        # Modify shared state
        # Other threads wait here
        pass
```

### Spin Lock vs Blocking Lock

```
SPIN LOCK:                          BLOCKING LOCK (Mutex):
  while not acquired:                 if not acquired:
      pass  # busy-wait (burns CPU)     OS.suspend(this_thread)
                                        # Thread sleeps, no CPU usage
  ✅ No context switch overhead         OS.wake(this_thread) when available
  ❌ Wastes CPU cycles                ✅ No CPU waste
  Best: very short critical sections  Best: longer critical sections
  
  Python: not built-in               Python: threading.Lock()
  Used in: OS kernels, embedded      Used in: application code
```

---

## Read-Write Lock

Allows **multiple concurrent readers** but only **one exclusive writer**.

```
                    ┌──────────────────┐
  Reader 1 ──read──→│                  │
  Reader 2 ──read──→│  Shared data     │  ← Multiple readers OK
  Reader 3 ──read──→│                  │
                    └──────────────────┘

  Writer ──write──→ │  Shared data     │  ← Only ONE writer,
                    │  (exclusive)     │     NO readers allowed
                    └──────────────────┘
```

```python
import threading

class ReadWriteLock:
    """Simple Read-Write Lock implementation"""
    
    def __init__(self):
        self._read_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._readers = 0
    
    def acquire_read(self):
        with self._read_lock:
            self._readers += 1
            if self._readers == 1:
                self._write_lock.acquire()  # First reader blocks writers
    
    def release_read(self):
        with self._read_lock:
            self._readers -= 1
            if self._readers == 0:
                self._write_lock.release()  # Last reader allows writers
    
    def acquire_write(self):
        self._write_lock.acquire()    # Exclusive access
    
    def release_write(self):
        self._write_lock.release()

# Usage
rw_lock = ReadWriteLock()

def reader(data, lock):
    lock.acquire_read()
    try:
        print(f"Reading: {data}")
    finally:
        lock.release_read()

def writer(data, new_value, lock):
    lock.acquire_write()
    try:
        data['value'] = new_value
        print(f"Written: {new_value}")
    finally:
        lock.release_write()
```

| Lock Type | Use Case | Throughput |
|-----------|----------|-----------|
| **Mutex** | Equal read/write ratio | Lower (all operations exclusive) |
| **RW Lock** | Read-heavy workloads | Higher (parallel readers) |

> **Caveat:** RW locks have **writer starvation** risk — continuous readers may prevent the writer from ever acquiring the lock. Solutions: writer-preference RW lock, or upgrade read → write lock.

---

## Atomic Operations

An **atomic operation** completes in a single step — no other thread can see a partial state.

```python
# In Python, these are atomic (due to GIL, single bytecode):
x = 42              # STORE_FAST (atomic)
y = x               # LOAD_FAST + STORE_FAST (atomic individually)
lst.append(item)    # Single bytecode operation
d[key] = value      # Single bytecode operation

# These are NOT atomic (multiple bytecodes):
x += 1              # LOAD + ADD + STORE (3 operations)
x = x + 1           # Same: 3 operations
d[key] += 1          # Multiple operations
if key in d:         # Check-then-act (TOCTOU race)
    d[key] += 1
```

### Python's Threading-Safe Atomic-Like Structures

```python
import queue
import collections

# thread-safe queue
q = queue.Queue()           # FIFO
q.put(item)                 # Thread-safe put
item = q.get()              # Thread-safe get

# collections.deque
d = collections.deque()
d.append(item)              # Thread-safe (atomic under GIL)
item = d.popleft()          # Thread-safe

# But for true atomicity in multi-threaded counter:
# Use threading.Lock or...
```

---

## Compare-And-Swap (CAS)

The fundamental building block of **lock-free** programming.

```
CAS(address, expected, new_value):
  atomically:
    if *address == expected:
        *address = new_value
        return True     # Success
    else:
        return False    # Someone else changed it — retry!

Usage pattern (lock-free increment):
  while True:
      old_value = read(counter)
      new_value = old_value + 1
      if CAS(&counter, old_value, new_value):
          break    # Success!
      # Otherwise: retry (another thread beat us)
```

> Python doesn't have native CAS, but many concurrent data structures use it internally (e.g., Java's `AtomicInteger`, Go's `sync/atomic`).

---

## Common Synchronization Problems

### 1. Producer-Consumer Problem

```python
import threading
import queue
import time
import random

buffer = queue.Queue(maxsize=5)

def producer():
    for i in range(10):
        item = f"item-{i}"
        buffer.put(item)  # Blocks if buffer full
        print(f"Produced: {item} (size={buffer.qsize()})")
        time.sleep(random.uniform(0.1, 0.5))

def consumer():
    while True:
        item = buffer.get()  # Blocks if buffer empty
        print(f"Consumed: {item}")
        buffer.task_done()
        time.sleep(random.uniform(0.2, 0.8))

# Start threads
threading.Thread(target=producer, daemon=True).start()
threading.Thread(target=consumer, daemon=True).start()
```

### 2. Readers-Writers Problem

Multiple readers can read simultaneously, but writers need exclusive access. (See RW Lock above.)

### 3. Dining Philosophers Problem

```
5 philosophers sit around a table.
Each needs 2 forks to eat.
Each fork shared between neighbors.

       P1
     /    \
   F5      F1
   /        \
  P5        P2
   \        /
   F4      F2
     \    /
       P3
      / \
    F3   (F2 shared with P2)

Naive: each picks up left fork first → DEADLOCK!
  All hold left, wait for right → circular wait

Solutions:
  1. Lock ordering: Pick up lower-numbered fork first
  2. Arbitrator: Central mutex before picking up any fork
  3. Limit seated: Allow at most 4 philosophers to sit
```

```python
import threading
import time
import random

forks = [threading.Lock() for _ in range(5)]

def philosopher(i):
    left = i
    right = (i + 1) % 5
    
    # Fix: always pick up lower-numbered fork first
    first, second = (min(left, right), max(left, right))
    
    for _ in range(3):
        # Think
        time.sleep(random.uniform(0.1, 0.5))
        
        # Eat (acquire both forks)
        with forks[first]:
            with forks[second]:
                print(f"Philosopher {i} is eating")
                time.sleep(random.uniform(0.1, 0.3))
        
        print(f"Philosopher {i} finished eating")

threads = [threading.Thread(target=philosopher, args=(i,)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()
```

---

## Memory Ordering and Visibility

In lower-level languages (C, C++, Java, Go), memory ordering matters because CPUs reorder instructions.

```
Thread 1:                Thread 2:
  x = 1                   while not flag:
  flag = True                 pass
                           print(x)  # x might be 0!

Why? CPU may reorder: flag=True BEFORE x=1 at hardware level.

Solutions:
  - Memory barriers / fences
  - Volatile variables (Java)
  - Atomic operations with ordering guarantees
  - In Python: GIL provides implicit memory barrier
```

### Python's GIL as Implicit Synchronization

```python
# In CPython, the GIL acts as a memory barrier between bytecodes.
# This means:
#   1. You don't need volatile or memory fences
#   2. Single bytecode operations are atomic
#   3. BUT compound operations still need locks

# Still UNSAFE (compound, not single bytecode):
counter += 1

# SAFE (GIL makes single bytecode atomic):
lst.append(item)
d[key] = val
```

---

## Interview Questions — Synchronization

### Q1: What is the difference between a mutex and a semaphore?

| Feature | Mutex | Semaphore |
|---------|-------|-----------|
| Access | Binary (1 thread) | Counting (N threads) |
| Ownership | Yes (only holder can release) | No (any thread can release) |
| Purpose | Protect shared resource | Limit concurrent access |
| Example | Protect a counter | Connection pool (max 10) |

### Q2: What is a deadlock? Give a real-world example.

Two threads each hold one lock and wait for the other's lock — circular dependency, both block forever.

**Real-world:** Thread A locks user table, then tries to lock order table. Thread B locks order table, then tries to lock user table. Both are stuck.

**Fix:** Always lock tables in alphabetical order (consistent lock ordering).

### Q3: What is the "check-then-act" race condition?

```python
# RACE: another thread may insert between check and act
if key not in cache:        # CHECK
    cache[key] = compute()  # ACT — another thread may have inserted!

# FIX: use setdefault or lock
with lock:
    if key not in cache:
        cache[key] = compute()
```

This is also called **TOCTOU** (Time-Of-Check to Time-Of-Use).

### Q4: Explain lock-free programming.

Lock-free algorithms use **atomic operations** (CAS) instead of locks. At least one thread makes progress at all times (no deadlock possible). Trade-off: more complex code, harder to reason about, but better performance under contention.
