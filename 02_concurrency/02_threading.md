# Threading in Python

## The `threading` Module

```python
import threading

def worker(name, duration):
    import time
    print(f"{name} starting")
    time.sleep(duration)
    print(f"{name} done")

# Create and start threads
t1 = threading.Thread(target=worker, args=("Thread-1", 2))
t2 = threading.Thread(target=worker, args=("Thread-2", 1))

t1.start()  # Start thread (non-blocking)
t2.start()

t1.join()   # Wait for thread to finish
t2.join()

print("All done")  # Runs after both threads complete
```

### Thread Properties

```python
t = threading.Thread(target=worker, args=("T1", 2))
t.daemon = True       # Daemon thread: killed when main thread exits
t.name = "MyThread"   # Name for debugging
t.start()

print(t.is_alive())   # True if thread is running
print(t.ident)         # Thread ID
print(t.native_id)     # OS-level thread ID

# Current thread info
print(threading.current_thread().name)
print(threading.active_count())
print(threading.enumerate())  # List all alive threads
```

### Daemon Threads

```python
import threading
import time

def background_job():
    while True:
        print("Background work...")
        time.sleep(1)

# Daemon thread: killed when main thread exits
t = threading.Thread(target=background_job, daemon=True)
t.start()

time.sleep(3)
print("Main thread exiting")
# Daemon thread automatically killed here — no need to stop it
```

| Aspect | Daemon Thread | Non-Daemon Thread |
|--------|--------------|-------------------|
| Lifecycle | Killed when main exits | Must finish before program exits |
| Use case | Background tasks (monitoring, logging) | Critical work (must complete) |
| Default | `daemon=False` | `daemon=False` |

---

## Locks

### Lock (Mutex)

Only **one thread** can hold the lock at a time.

```python
import threading

lock = threading.Lock()
balance = 0

def deposit(amount):
    global balance
    
    # Method 1: Context manager (preferred — auto-releases)
    with lock:
        balance += amount
    
    # Method 2: Manual acquire/release
    lock.acquire()
    try:
        balance += amount
    finally:
        lock.release()  # Always release in finally!

    # Method 3: Non-blocking try-lock
    if lock.acquire(blocking=False):
        try:
            balance += amount
        finally:
            lock.release()
    else:
        print("Lock busy, skipping")

    # Method 4: Timeout
    if lock.acquire(timeout=5):
        try:
            balance += amount
        finally:
            lock.release()
    else:
        print("Timeout waiting for lock")
```

### RLock (Reentrant Lock)

A lock that the **same thread** can acquire multiple times without deadlocking.

```python
import threading

lock = threading.Lock()
rlock = threading.RLock()

# Lock — DEADLOCK! (same thread acquires twice)
def bad():
    with lock:
        with lock:        # ← DEADLOCK! Lock is already held
            print("never reaches here")

# RLock — works fine (same thread can re-acquire)
def good():
    with rlock:
        with rlock:        # ← OK! RLock tracks acquisition count
            print("this works!")
    # Must release same number of times as acquired
```

**When to use RLock:**
- Recursive functions that need locking
- When a locked method calls another locked method (on the same object)

```python
class BankAccount:
    def __init__(self):
        self.balance = 0
        self._lock = threading.RLock()
    
    def deposit(self, amount):
        with self._lock:
            self.balance += amount
    
    def withdraw(self, amount):
        with self._lock:
            self.balance -= amount
    
    def transfer(self, other, amount):
        with self._lock:             # Acquires lock
            self.withdraw(amount)     # Re-acquires lock (RLock allows this)
            other.deposit(amount)
```

---

## Semaphore

Allows up to **N threads** to access a resource simultaneously.

```python
import threading
import time

# Max 3 concurrent connections
semaphore = threading.Semaphore(3)

def connect_to_db(thread_id):
    with semaphore:  # Blocks if 3 threads already inside
        print(f"Thread {thread_id}: connected")
        time.sleep(2)  # Simulate query
        print(f"Thread {thread_id}: disconnected")

# 10 threads, but only 3 run concurrently
threads = []
for i in range(10):
    t = threading.Thread(target=connect_to_db, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

### BoundedSemaphore

Like Semaphore, but **raises error** if released more times than acquired (catches bugs).

```python
sem = threading.BoundedSemaphore(3)
sem.acquire()
sem.release()
sem.release()  # ← ValueError! Released more than acquired
               # Regular Semaphore would silently allow this
```

---

## Event

A flag that threads can **wait on** and **set/clear**.

```python
import threading
import time

ready_event = threading.Event()

def consumer():
    print("Consumer waiting for data...")
    ready_event.wait()          # Block until event is set
    print("Consumer: data is ready, processing!")

def producer():
    print("Producer preparing data...")
    time.sleep(2)
    print("Producer: data ready!")
    ready_event.set()           # Wake up ALL waiting threads

t1 = threading.Thread(target=consumer)
t2 = threading.Thread(target=consumer)
t3 = threading.Thread(target=producer)

t1.start(); t2.start(); t3.start()
# Both consumers wake up when producer calls set()
```

```python
# Wait with timeout
ready_event.wait(timeout=5)  # Returns True if set, False if timeout

# Reset event
ready_event.clear()          # Reset to unset (threads will block on wait again)
ready_event.is_set()         # Check without blocking
```

---

## Condition

Combines a **lock** with the ability to **wait for a condition** to become true.

```python
import threading
import time

buffer = []
MAX_SIZE = 5
condition = threading.Condition()

def producer():
    for i in range(10):
        with condition:
            while len(buffer) >= MAX_SIZE:
                condition.wait()          # Release lock and wait
            buffer.append(i)
            print(f"Produced: {i}, buffer: {buffer}")
            condition.notify()            # Wake one waiting consumer

def consumer():
    for _ in range(10):
        with condition:
            while len(buffer) == 0:
                condition.wait()          # Release lock and wait
            item = buffer.pop(0)
            print(f"Consumed: {item}, buffer: {buffer}")
            condition.notify()            # Wake one waiting producer
        time.sleep(0.1)

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
```

| Method | Description |
|--------|-------------|
| `wait()` | Release lock, block until notified, re-acquire lock |
| `wait_for(predicate)` | Wait until predicate returns True |
| `notify(n=1)` | Wake up n waiting threads |
| `notify_all()` | Wake up ALL waiting threads |

---

## Barrier

Synchronization point where threads **wait for each other** before proceeding.

```python
import threading
import time

barrier = threading.Barrier(3)  # Wait for 3 threads

def worker(name):
    print(f"{name}: preparing...")
    time.sleep(1)
    print(f"{name}: waiting at barrier...")
    barrier.wait()              # Block until all 3 arrive
    print(f"{name}: proceeding!")  # All 3 print this ~simultaneously

for name in ["A", "B", "C"]:
    threading.Thread(target=worker, args=(name,)).start()
```

---

## Timer

Execute a function **after a delay**.

```python
import threading

def reminder():
    print("Time's up!")

timer = threading.Timer(5.0, reminder)  # Call after 5 seconds
timer.start()
timer.cancel()  # Cancel before it fires
```

---

## Thread Pools: `concurrent.futures`

High-level interface for running tasks in thread or process pools.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def fetch_url(url):
    time.sleep(1)  # Simulate HTTP request
    return f"Response from {url}"

urls = [f"https://api.example.com/data/{i}" for i in range(10)]

# ThreadPoolExecutor — manages a pool of threads
with ThreadPoolExecutor(max_workers=5) as executor:
    # Method 1: map (ordered results)
    results = executor.map(fetch_url, urls)
    for result in results:
        print(result)

    # Method 2: submit + as_completed (results as they finish)
    futures = {executor.submit(fetch_url, url): url for url in urls}
    for future in as_completed(futures):
        url = futures[future]
        try:
            result = future.result()
            print(f"{url}: {result}")
        except Exception as e:
            print(f"{url}: error {e}")
```

### Future Object

```python
from concurrent.futures import ThreadPoolExecutor

def slow_task(n):
    import time; time.sleep(n)
    return n * 2

with ThreadPoolExecutor() as executor:
    future = executor.submit(slow_task, 3)
    
    print(future.done())          # False (still running)
    print(future.running())       # True
    
    result = future.result(timeout=10)  # Block until done (or timeout)
    print(result)                 # 6
    
    print(future.done())          # True
    print(future.cancelled())     # False
    
    # Cancel (only works if not yet running)
    future2 = executor.submit(slow_task, 5)
    future2.cancel()              # Returns True if successfully cancelled
```

### Practical Example: Concurrent API Calls

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_user(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

user_ids = range(1, 101)  # Fetch 100 users

with ThreadPoolExecutor(max_workers=20) as executor:
    future_to_id = {executor.submit(fetch_user, uid): uid for uid in user_ids}
    
    users = []
    errors = []
    
    for future in as_completed(future_to_id):
        uid = future_to_id[future]
        try:
            users.append(future.result())
        except Exception as e:
            errors.append((uid, str(e)))

print(f"Fetched {len(users)} users, {len(errors)} errors")
# Sequential: ~100 seconds (1s per request)
# With 20 workers: ~5 seconds (20 concurrent requests)
```

---

## Interview Questions — Threading

### Q1: Why use a thread pool instead of creating threads manually?

1. **Reuse threads** — creating/destroying threads is expensive
2. **Limit concurrency** — prevent resource exhaustion (1000 threads = 1000 sockets)
3. **Simpler API** — `executor.map()` vs manual thread management
4. **Error handling** — `Future` objects capture exceptions

### Q2: What is the difference between Lock and RLock?

| Feature | Lock | RLock |
|---------|------|-------|
| Same thread re-acquire | ❌ Deadlocks | ✅ Allowed |
| Overhead | Slightly less | Tracks owner + count |
| Use case | Simple mutual exclusion | Recursive/nested locking |

### Q3: When would you use a Semaphore vs a Lock?

- **Lock (Mutex):** Only 1 thread at a time (exclusive access)
- **Semaphore(N):** Up to N threads at a time (rate limiting, connection pools)

Example: Database connection pool with max 10 connections → `Semaphore(10)`
