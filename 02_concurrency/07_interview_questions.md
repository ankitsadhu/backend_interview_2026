# Concurrency Interview Questions

> Comprehensive question bank covering beginner to advanced topics, rapid-fire, and coding challenges.

---

## 🟢 Beginner Level

### Q1: What is the difference between concurrency and parallelism?

**Concurrency:** Dealing with multiple things at once (structure). Tasks can make progress by interleaving on a single core.

**Parallelism:** Doing multiple things at once (execution). Tasks literally run simultaneously on multiple cores.

**Analogy:** One chef handling 3 dishes (switching between them) = concurrency. Three chefs each cooking one dish = parallelism.

---

### Q2: What is the GIL?

The **Global Interpreter Lock** is a mutex in CPython that allows only one thread to execute Python bytecode at a time, even on multi-core machines.

**Impact:** Multi-threaded Python code can't achieve true parallelism for CPU-bound tasks.

**Workarounds:**
1. `multiprocessing` (separate processes, each with own GIL)
2. `asyncio` (GIL released during I/O waits)
3. C extensions that release the GIL (NumPy)
4. Free-threaded Python 3.13+ (experimental)

---

### Q3: What is a race condition?

When the result of a program depends on the **timing of thread execution**. Two threads access shared data without proper synchronization, and the final state is unpredictable.

```python
# Race condition: counter += 1 is NOT atomic
# Read(100) → Read(100) → Write(101) → Write(101)
# Two increments, but counter only goes up by 1!
```

**Fix:** Use `threading.Lock()` to make the operation atomic.

---

### Q4: What is a deadlock?

When two or more threads are **waiting for each other** to release resources, creating a circular dependency.

**Four conditions** (all required):
1. Mutual exclusion
2. Hold and wait
3. No preemption
4. Circular wait

**Fix:** Lock ordering (always acquire in the same order).

---

### Q5: When should you use threads vs processes vs async?

| Workload | Best Approach | Why |
|----------|--------------|-----|
| **I/O-bound** (HTTP, DB, files) | `asyncio` or `threading` | GIL released during I/O |
| **CPU-bound** (math, encoding) | `multiprocessing` | Bypasses GIL |
| **Many concurrent connections** | `asyncio` | ~1 KB/coroutine vs ~8 MB/thread |
| **Simple scripting** | `threading` | Easiest API |

---

## 🟡 Intermediate Level

### Q6: Explain async/await. How does it differ from threading?

| Aspect | Threading | Async/Await |
|--------|----------|-------------|
| Switching | **Preemptive** (OS decides) | **Cooperative** (code yields at `await`) |
| Threads | Multiple OS threads | Single thread |
| Race conditions | Possible | Rare (single thread) |
| Memory | ~8 MB per thread | ~1 KB per coroutine |
| Scalability | ~1,000 threads | ~100,000+ coroutines |
| Blocking code | OK (each thread can block) | Must use `await` (blocking freezes everything) |

---

### Q7: What is `concurrent.futures` and when do you use it?

A **high-level interface** providing `ThreadPoolExecutor` and `ProcessPoolExecutor` with the same API:

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Same API for both!
with ThreadPoolExecutor(max_workers=10) as exe:  # I/O-bound
    future = exe.submit(function, arg)
    result = future.result()

with ProcessPoolExecutor(max_workers=4) as exe:  # CPU-bound
    results = list(exe.map(function, iterable))
```

**Benefits:** Consistent API, `Future` objects for error handling, easy to switch between threads and processes.

---

### Q8: What is a semaphore? Give a real-world use case.

A semaphore allows up to **N threads** to access a resource simultaneously (vs mutex which allows 1).

**Use case:** Database connection pool with max 10 connections:

```python
pool_semaphore = threading.Semaphore(10)

def query_db(sql):
    with pool_semaphore:  # Max 10 concurrent queries
        conn = get_connection()
        return conn.execute(sql)
```

---

### Q9: What is the difference between `asyncio.gather` and `TaskGroup`?

| Feature | `gather` | `TaskGroup` (3.11+) |
|---------|----------|---------------------|
| Error handling | `return_exceptions=True` or cancels all | `ExceptionGroup` (automatic) |
| Cancellation | No automatic cleanup | Auto-cancels all on exception |
| Structured | No (tasks can outlive scope) | Yes (all tasks scoped to `async with`) |
| Recommended | Simple cases | ✅ Modern best practice |

---

### Q10: How do you run blocking code inside asyncio?

```python
# Thread pool (for blocking I/O)
result = await asyncio.to_thread(blocking_function, arg)

# Process pool (for CPU-bound)
loop = asyncio.get_event_loop()
with ProcessPoolExecutor() as pool:
    result = await loop.run_in_executor(pool, cpu_function, arg)
```

Never call blocking functions directly in async code — they freeze the entire event loop.

---

### Q11: What is the producer-consumer pattern?

Producers generate work items and place them in a **shared buffer** (queue). Consumers take items and process them. The queue decouples production and consumption rates.

**Python implementations:**
- `queue.Queue` (threading)
- `asyncio.Queue` (asyncio)
- `multiprocessing.Queue` (processes)

---

## 🔴 Advanced Level

### Q12: Explain the Actor model. How does it avoid race conditions?

Each actor has:
- **Private state** (never shared)
- **Mailbox** (queue of incoming messages)
- Processes **one message at a time** (sequential)

No shared state → no locks → no race conditions.

**Trade-off:** Communication overhead (serialization/deserialization of messages) vs simplicity.

Used by: Erlang/OTP, Akka, Elixir.

---

### Q13: What is cooperative vs preemptive multitasking?

| Aspect | Cooperative (asyncio) | Preemptive (threading) |
|--------|----------------------|----------------------|
| Switching | Task voluntarily yields (`await`) | OS interrupts at any point |
| Control | Developer controls yields | OS controls scheduling |
| Race conditions | Rare (switch only at `await`) | Common (switch anytime) |
| Starvation | Easy (long sync code blocks all) | Less likely (OS is fair) |

---

### Q14: How does Python's asyncio event loop work internally?

```
1. Event loop checks for ready callbacks (scheduled tasks)
2. Calls select()/epoll()/kqueue() to check for I/O readiness
3. For each ready I/O event:
   - Resume the corresponding coroutine
   - Coroutine runs until next `await`
   - Coroutine yields control back to event loop
4. Process timers and scheduled callbacks
5. Repeat from step 1
```

The event loop is essentially the **Reactor pattern**: a single thread multiplexing I/O events and dispatching to handlers (coroutines).

---

### Q15: What is the Dining Philosophers problem?

5 philosophers need 2 forks to eat. Each fork is shared with a neighbor. Naive solution (pick up left then right) → deadlock when all pick up left simultaneously.

**Solutions:**
1. **Lock ordering:** Always pick up lower-numbered fork first
2. **Arbitrator:** Global mutex before picking up any fork
3. **Resource limit:** Allow at most N-1 philosophers to sit at once

---

### Q16: Compare threading.Lock, queue.Queue, and asyncio patterns.

| Need | Solution |
|------|---------|
| Protect shared variable | `threading.Lock` |
| Thread-safe data passing | `queue.Queue` |
| Limit concurrent access | `threading.Semaphore(N)` |
| Wait for condition | `threading.Condition` |
| Signal across threads | `threading.Event` |
| Async data passing | `asyncio.Queue` |
| Async mutual exclusion | `asyncio.Lock` |
| Async rate limiting | `asyncio.Semaphore` |

---

## ⚡ Rapid-Fire Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | GIL stands for? | Global Interpreter Lock |
| 2 | Does the GIL affect multiprocessing? | No — each process has its own GIL |
| 3 | Is `list.append()` thread-safe in Python? | Yes (single bytecode under GIL) |
| 4 | Is `counter += 1` thread-safe? | No (read + increment + write = 3 bytecodes) |
| 5 | What does `join()` do on a thread? | Blocks until that thread completes |
| 6 | Daemon thread vs non-daemon? | Daemon killed when main exits; non-daemon must finish |
| 7 | `Lock` vs `RLock`? | RLock can be re-acquired by the same thread |
| 8 | What is `asyncio.run()`? | Creates event loop, runs coroutine, closes loop |
| 9 | Can you mix `time.sleep()` and asyncio? | No — it blocks the event loop. Use `asyncio.sleep()` |
| 10 | What is a `Future`? | A placeholder for a result that hasn't been computed yet |
| 11 | `map` vs `submit` in `ThreadPoolExecutor`? | `map` = ordered results, `submit` = returns `Future` |
| 12 | Why is `if __name__ == "__main__"` needed for multiprocessing? | Prevents infinite process spawning on Windows (spawn start method) |
| 13 | What is `asyncio.to_thread`? | Runs blocking function in a thread pool from async code |
| 14 | What is a coroutine? | An async function that can be paused and resumed at `await` points |
| 15 | Semaphore(1) == Lock? | Similar, but semaphore has no ownership (anyone can release) |
| 16 | What is starvation? | A thread never gets access because others keep acquiring first |
| 17 | What is livelock? | Threads keep changing state in response to each other but no progress |
| 18 | Event loop runs on how many threads? | 1 thread (single-threaded) |
| 19 | `gather` vs `wait`? | `gather` returns ordered results; `wait` returns done/pending sets |
| 20 | What is structured concurrency? | Tasks have a clear scope and lifetime (TaskGroup in Python 3.11+) |

---

## 🧑‍💻 Coding Challenges

### Challenge 1: Thread-Safe Counter

Implement a class that can be safely incremented from multiple threads.

```python
import threading

class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
    
    def decrement(self):
        with self._lock:
            self._value -= 1
    
    @property
    def value(self):
        with self._lock:
            return self._value

# Test
counter = ThreadSafeCounter()
threads = [threading.Thread(target=counter.increment) for _ in range(10_000)]
for t in threads: t.start()
for t in threads: t.join()
assert counter.value == 10_000
```

---

### Challenge 2: Bounded Buffer (Producer-Consumer)

```python
import asyncio
import random

class BoundedBuffer:
    def __init__(self, capacity):
        self._queue = asyncio.Queue(maxsize=capacity)
    
    async def put(self, item):
        await self._queue.put(item)
    
    async def get(self):
        return await self._queue.get()
    
    def size(self):
        return self._queue.qsize()

async def producer(buf, n):
    for i in range(n):
        await buf.put(i)
        print(f"Produced: {i}")
        await asyncio.sleep(random.uniform(0.01, 0.1))

async def consumer(buf, n):
    for _ in range(n):
        item = await buf.get()
        print(f"Consumed: {item}")
        await asyncio.sleep(random.uniform(0.02, 0.15))

async def main():
    buf = BoundedBuffer(capacity=5)
    await asyncio.gather(
        producer(buf, 20),
        consumer(buf, 20),
    )

asyncio.run(main())
```

---

### Challenge 3: Rate-Limited Async Fetcher

```python
import asyncio
import aiohttp
import time

class RateLimitedFetcher:
    def __init__(self, max_concurrent=10, requests_per_second=5):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._rate_limit = 1.0 / requests_per_second
        self._last_request_time = 0
        self._rate_lock = asyncio.Lock()
    
    async def fetch(self, session, url):
        # Rate limiting
        async with self._rate_lock:
            now = time.monotonic()
            wait = self._rate_limit - (now - self._last_request_time)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request_time = time.monotonic()
        
        # Concurrency limiting
        async with self._semaphore:
            async with session.get(url) as response:
                return await response.text()
    
    async def fetch_all(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, url) for url in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)
```

---

### Challenge 4: Parallel Map-Reduce

```python
from concurrent.futures import ProcessPoolExecutor
import math

def map_function(chunk):
    """Map: count primes in chunk"""
    count = 0
    for n in chunk:
        if n < 2:
            continue
        if all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1)):
            count += 1
    return count

def parallel_count_primes(limit, num_workers=4):
    """Count primes up to 'limit' using map-reduce"""
    # Split into chunks
    chunk_size = limit // num_workers
    chunks = [
        range(i, min(i + chunk_size, limit))
        for i in range(0, limit, chunk_size)
    ]
    
    # Map (parallel)
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        partial_counts = list(executor.map(map_function, chunks))
    
    # Reduce (combine)
    return sum(partial_counts)

if __name__ == "__main__":
    total = parallel_count_primes(1_000_000, num_workers=4)
    print(f"Primes under 1M: {total}")  # 78498
```
