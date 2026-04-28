# Asyncio (Asynchronous I/O)

## What is Asyncio?

**asyncio** is Python's built-in library for writing **single-threaded concurrent** code using **coroutines**, event loops, and non-blocking I/O.

```
Threading (multiple threads):            Asyncio (single thread, cooperative):
┌────────────────────────────┐          ┌────────────────────────────┐
│ Thread 1: ██░░░░██░░░░██  │          │ Event Loop:                │
│ Thread 2: ░░██░░░░██░░░░  │          │  task1: ██..........██     │
│ Thread 3: ░░░░██░░░░██░░  │          │  task2: ..██........  ██   │
│                            │          │  task3: ....██......    ██ │
│ OS manages switching       │          │                            │
│ (preemptive)               │          │  Tasks yield at await      │
│                            │          │  (cooperative)             │
└────────────────────────────┘          └────────────────────────────┘
                                          █ = running  . = waiting (I/O)
```

| Aspect | Threading | Asyncio |
|--------|----------|---------|
| Concurrency model | Preemptive (OS switches threads) | Cooperative (tasks yield at `await`) |
| Threads | Multiple OS threads | Single thread |
| Context switches | OS-managed (expensive) | In-process (cheap) |
| Race conditions | Possible (shared state + preemption) | Rare (single thread, explicit yields) |
| Memory per task | ~8 MB stack per thread | ~1 KB per coroutine |
| Scalability | ~1000 threads | ~100,000+ coroutines |
| Best for | I/O-bound with blocking libs | I/O-bound with async libs |

---

## Coroutines and `async`/`await`

```python
import asyncio

# Define a coroutine (async function)
async def greet(name, delay):
    print(f"Hello, {name}!")
    await asyncio.sleep(delay)     # Non-blocking sleep (yields to event loop)
    print(f"Goodbye, {name}!")
    return f"Done: {name}"

# Running coroutines
async def main():
    # Sequential (no concurrency!)
    result1 = await greet("Alice", 2)    # Wait 2 seconds
    result2 = await greet("Bob", 1)      # Then wait 1 second
    # Total: 3 seconds

    # Concurrent (with gather)
    result1, result2 = await asyncio.gather(
        greet("Alice", 2),
        greet("Bob", 1),
    )
    # Total: 2 seconds (runs concurrently!)

# Entry point
asyncio.run(main())
```

### Key Rules

```python
# 1. async def creates a coroutine FUNCTION
async def my_coroutine():
    pass

# 2. Calling it returns a coroutine OBJECT (doesn't execute!)
coro = my_coroutine()  # Nothing happens yet!

# 3. Must be awaited or scheduled to execute
await my_coroutine()   # Executes and waits for result

# 4. await can ONLY be used inside async functions
def sync_function():
    await my_coroutine()  # ❌ SyntaxError!

# 5. Don't use blocking calls in async code!
async def bad():
    import time
    time.sleep(5)        # ❌ Blocks the ENTIRE event loop!
    
async def good():
    await asyncio.sleep(5)  # ✅ Non-blocking (yields to event loop)
```

---

## Tasks

Tasks run coroutines **concurrently** in the event loop.

```python
import asyncio

async def fetch_data(url, delay):
    print(f"Fetching {url}...")
    await asyncio.sleep(delay)
    return f"Data from {url}"

async def main():
    # Create tasks (start running immediately!)
    task1 = asyncio.create_task(fetch_data("url1", 2))
    task2 = asyncio.create_task(fetch_data("url2", 1))
    task3 = asyncio.create_task(fetch_data("url3", 3))
    
    # Await results
    result1 = await task1
    result2 = await task2
    result3 = await task3
    
    print(result1, result2, result3)
    # All 3 run concurrently → total ~3 seconds (not 6!)

asyncio.run(main())
```

### Task vs Coroutine

```python
# Coroutine: awaited directly — runs when YOU await it
await fetch_data("url1", 2)   # Blocks here until complete

# Task: scheduled in event loop — starts running immediately
task = asyncio.create_task(fetch_data("url1", 2))  # Started!
# ... do other work ...
result = await task   # Get result when ready
```

---

## `asyncio.gather` vs `asyncio.wait` vs `TaskGroup`

### gather

```python
# Run multiple coroutines concurrently, return ALL results (ordered)
results = await asyncio.gather(
    fetch_data("url1", 2),
    fetch_data("url2", 1),
    fetch_data("url3", 3),
    return_exceptions=True,  # Don't cancel on first exception
)
# results = [result1, result2, result3] (same order as input)
```

### wait

```python
# More control over completion
tasks = [
    asyncio.create_task(fetch_data(f"url{i}", i))
    for i in range(5)
]

# Wait for first to complete
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
for task in done:
    print(task.result())

# Wait for all
done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

# Wait with timeout
done, pending = await asyncio.wait(tasks, timeout=3.0)
for task in pending:
    task.cancel()  # Cancel remaining
```

### TaskGroup (Python 3.11+ — Structured Concurrency)

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data("url1", 2))
        task2 = tg.create_task(fetch_data("url2", 1))
        task3 = tg.create_task(fetch_data("url3", 3))
    
    # All tasks guaranteed complete here
    # If ANY task raises → all others cancelled → ExceptionGroup raised
    print(task1.result(), task2.result(), task3.result())
```

| Feature | `gather` | `wait` | `TaskGroup` |
|---------|----------|--------|-------------|
| Returns | List of results | (done, pending) sets | Results via task objects |
| Error handling | `return_exceptions=True` | Manual | ExceptionGroup (automatic) |
| Cancellation | All-or-nothing | Manual | Automatic on exception |
| Structured | No | No | ✅ Yes (Python 3.11+) |
| Recommended | Simple cases | Advanced control | ✅ Modern best practice |

---

## Timeouts and Cancellation

```python
# Timeout
async def main():
    try:
        result = await asyncio.wait_for(
            fetch_data("slow_url", 10),
            timeout=3.0
        )
    except asyncio.TimeoutError:
        print("Request timed out!")

    # Timeout context (Python 3.11+)
    async with asyncio.timeout(3.0):
        result = await fetch_data("slow_url", 10)

# Cancel a task
async def main():
    task = asyncio.create_task(fetch_data("url", 10))
    await asyncio.sleep(2)
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        print("Task was cancelled")
```

---

## Async Generators and Iterators

```python
# Async generator — yield values asynchronously
async def stream_data(n):
    for i in range(n):
        await asyncio.sleep(0.5)
        yield f"chunk-{i}"

async def main():
    async for chunk in stream_data(5):
        print(chunk)

# Async context manager
class AsyncDBConnection:
    async def __aenter__(self):
        self.conn = await connect_to_db()
        return self.conn
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

async def main():
    async with AsyncDBConnection() as conn:
        result = await conn.execute("SELECT * FROM users")
```

---

## Real-World: Async HTTP Requests with aiohttp

```python
import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [f"https://httpbin.org/delay/{i}" for i in range(1, 6)]
    
    async with aiohttp.ClientSession() as session:
        # Concurrent fetching
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for url, result in zip(urls, results):
            print(f"{url}: {len(result)} chars")

asyncio.run(main())
# Sequential: 1+2+3+4+5 = 15 seconds
# Concurrent: ~5 seconds (limited by slowest)
```

## Real-World: Async Database Queries with asyncpg

```python
import asyncio
import asyncpg

async def main():
    # Connection pool
    pool = await asyncpg.create_pool(
        "postgresql://user:pass@localhost/mydb",
        min_size=5,
        max_size=20
    )
    
    # Concurrent queries
    async with pool.acquire() as conn:
        users = await conn.fetch("SELECT * FROM users LIMIT 100")
        orders = await conn.fetch("SELECT * FROM orders LIMIT 100")
    
    # Or truly concurrent
    async with pool.acquire() as conn1, pool.acquire() as conn2:
        users_task = asyncio.create_task(conn1.fetch("SELECT * FROM users"))
        orders_task = asyncio.create_task(conn2.fetch("SELECT * FROM orders"))
        users, orders = await asyncio.gather(users_task, orders_task)
    
    await pool.close()

asyncio.run(main())
```

---

## Running Blocking Code in Async

```python
import asyncio
import time

def blocking_io():
    """Simulates blocking I/O (library that doesn't support async)"""
    time.sleep(2)
    return "result"

def cpu_intensive():
    """CPU-bound computation"""
    return sum(i * i for i in range(10_000_000))

async def main():
    loop = asyncio.get_event_loop()
    
    # Run blocking I/O in thread pool (don't block event loop!)
    result = await loop.run_in_executor(None, blocking_io)  # None = default ThreadPool
    
    # Run CPU-bound in process pool
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_intensive)
    
    # Shorthand (Python 3.9+)
    result = await asyncio.to_thread(blocking_io)

asyncio.run(main())
```

---

## Asyncio Synchronization Primitives

```python
# Lock (async version)
lock = asyncio.Lock()
async with lock:
    # Critical section

# Semaphore (limit concurrency)
sem = asyncio.Semaphore(10)  # Max 10 concurrent
async with sem:
    await fetch_url(url)

# Event
event = asyncio.Event()
await event.wait()     # Block until set
event.set()            # Wake all waiters
event.clear()          # Reset

# Queue (async producer-consumer)
queue = asyncio.Queue(maxsize=100)
await queue.put(item)  # Blocks if full
item = await queue.get()
queue.task_done()
await queue.join()      # Wait until all items processed
```

---

## Interview Questions — Asyncio

### Q1: When should you use asyncio vs threading?

| Scenario | Use |
|----------|-----|
| Many I/O tasks + async library available | **asyncio** (most scalable) |
| I/O tasks + only blocking libraries | **threading** (or `to_thread`) |
| Need 10,000+ concurrent connections | **asyncio** (~1KB per coroutine) |
| Simple script, few concurrent tasks | **threading** (easier) |
| CPU-bound work | **multiprocessing** (bypasses GIL) |

### Q2: What happens if you use `time.sleep()` in async code?

It **blocks the entire event loop**. No other coroutine can run during the sleep. All concurrent tasks freeze. Always use `await asyncio.sleep()` in async code — it yields control back to the event loop.

### Q3: What is structured concurrency (TaskGroup)?

A programming paradigm where concurrent tasks have a **clear scope and lifetime**. With `TaskGroup`, all tasks start inside the context, and the context doesn't exit until ALL tasks complete. If one fails, all others are cancelled automatically. This prevents "fire and forget" tasks that can leak resources.

### Q4: How do you handle 10,000 concurrent HTTP requests without overwhelming the server?

Use a **semaphore** to limit concurrency:

```python
sem = asyncio.Semaphore(100)  # Max 100 concurrent

async def bounded_fetch(url):
    async with sem:
        return await fetch_url(url)

results = await asyncio.gather(*[bounded_fetch(url) for url in urls])
```
