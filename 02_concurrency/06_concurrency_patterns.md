# Concurrency Patterns

## Producer-Consumer Pattern

The most fundamental concurrency pattern. One or more producers generate work, one or more consumers process it, connected by a **bounded buffer**.

```
┌──────────┐     ┌──────────────────┐     ┌──────────┐
│ Producer  │ ──→ │  Bounded Buffer   │ ──→ │ Consumer  │
│ Producer  │ ──→ │  (Queue)          │ ──→ │ Consumer  │
│ Producer  │ ──→ │  [■ ■ ■ □ □]     │ ──→ │ Consumer  │
└──────────┘     └──────────────────┘     └──────────┘
                  Blocks if full ↑          Blocks if empty
```

### Threading Implementation

```python
import threading
import queue
import time
import random

def producer(q, name, items):
    for i in range(items):
        item = f"{name}-item-{i}"
        q.put(item)         # Blocks if queue is full
        print(f"{name}: produced {item}")
        time.sleep(random.uniform(0.1, 0.3))
    q.put(None)             # Poison pill sentinel

def consumer(q, name):
    while True:
        item = q.get()      # Blocks if queue is empty
        if item is None:
            q.put(None)     # Pass sentinel to next consumer
            break
        print(f"{name}: consumed {item}")
        time.sleep(random.uniform(0.2, 0.5))
        q.task_done()

buffer = queue.Queue(maxsize=10)

producers = [threading.Thread(target=producer, args=(buffer, f"P{i}", 5)) for i in range(3)]
consumers = [threading.Thread(target=consumer, args=(buffer, f"C{i}")) for i in range(2)]

for t in producers + consumers: t.start()
for t in producers: t.join()
buffer.join()  # Wait until all items processed
```

### Asyncio Implementation

```python
import asyncio
import random

async def producer(q, name, items):
    for i in range(items):
        item = f"{name}-item-{i}"
        await q.put(item)
        print(f"{name}: produced {item}")
        await asyncio.sleep(random.uniform(0.1, 0.3))

async def consumer(q, name):
    while True:
        item = await q.get()
        print(f"{name}: consumed {item}")
        await asyncio.sleep(random.uniform(0.2, 0.5))
        q.task_done()

async def main():
    q = asyncio.Queue(maxsize=10)
    
    producers = [asyncio.create_task(producer(q, f"P{i}", 5)) for i in range(3)]
    consumers = [asyncio.create_task(consumer(q, f"C{i}")) for i in range(2)]
    
    await asyncio.gather(*producers)
    await q.join()       # Wait until all items processed
    
    for c in consumers:
        c.cancel()       # Stop consumers

asyncio.run(main())
```

---

## Worker Pool Pattern

A fixed pool of workers process tasks from a shared queue.

```
                    ┌──────────────────┐
  Task 1 ──────→   │                  │   ──→  Worker 1
  Task 2 ──────→   │   Task Queue     │   ──→  Worker 2
  Task 3 ──────→   │  [T4][T5][T6]    │   ──→  Worker 3
  Task 4 ──────→   │                  │   ──→  Worker 4
  ...              └──────────────────┘
```

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_task(task_id):
    import time
    time.sleep(0.5)
    return f"Result of task {task_id}"

# Pool of 4 workers processing 20 tasks
with ThreadPoolExecutor(max_workers=4) as pool:
    futures = {pool.submit(process_task, i): i for i in range(20)}
    
    for future in as_completed(futures):
        task_id = futures[future]
        print(f"Task {task_id}: {future.result()}")
```

---

## Fan-Out / Fan-In Pattern

**Fan-out:** Distribute work across multiple workers (parallel processing).
**Fan-in:** Collect and merge results from multiple workers.

```
               Fan-Out                          Fan-In
  ┌──────────┐    ┌──────────┐         ┌──────────┐
  │          │ ──→│ Worker 1  │──result→│          │
  │   Data   │ ──→│ Worker 2  │──result→│ Combiner │ ──→ Final Result
  │  Source  │ ──→│ Worker 3  │──result→│          │
  │          │ ──→│ Worker 4  │──result→│          │
  └──────────┘    └──────────┘         └──────────┘
```

```python
import asyncio

async def process_chunk(data_chunk):
    """Worker: process one chunk"""
    await asyncio.sleep(0.5)  # Simulate work
    return sum(data_chunk)

async def fan_out_fan_in(data, num_workers):
    # Fan-out: split data into chunks
    chunk_size = len(data) // num_workers
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Process all chunks concurrently
    tasks = [asyncio.create_task(process_chunk(chunk)) for chunk in chunks]
    
    # Fan-in: collect results
    results = await asyncio.gather(*tasks)
    
    # Combine
    return sum(results)

async def main():
    data = list(range(1_000_000))
    total = await fan_out_fan_in(data, num_workers=10)
    print(f"Total: {total}")

asyncio.run(main())
```

---

## Pipeline Pattern

Process data through a **series of stages**, each running concurrently.

```
  Stage 1        Stage 2        Stage 3        Stage 4
 (Extract)     (Transform)     (Enrich)       (Load)
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Read CSV  │→│ Clean data│→│ Add geo  │→│ Write DB  │
│           │  │ Validate  │  │ API call │  │           │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
      ↓ Queue      ↓ Queue      ↓ Queue
  Data flows through stages concurrently
  Each stage processes at its own speed
```

```python
import asyncio

async def stage_extract(output_q):
    """Stage 1: Read data"""
    for i in range(20):
        data = {"id": i, "raw": f"data-{i}"}
        await output_q.put(data)
        await asyncio.sleep(0.1)
    await output_q.put(None)

async def stage_transform(input_q, output_q):
    """Stage 2: Transform data"""
    while True:
        data = await input_q.get()
        if data is None:
            await output_q.put(None)
            break
        data["transformed"] = data["raw"].upper()
        await output_q.put(data)
        await asyncio.sleep(0.05)

async def stage_load(input_q):
    """Stage 3: Load data"""
    results = []
    while True:
        data = await input_q.get()
        if data is None:
            break
        results.append(data)
        print(f"Loaded: {data}")
    return results

async def main():
    q1 = asyncio.Queue(maxsize=5)
    q2 = asyncio.Queue(maxsize=5)
    
    # All stages run concurrently
    await asyncio.gather(
        stage_extract(q1),
        stage_transform(q1, q2),
        stage_load(q2),
    )

asyncio.run(main())
```

---

## Actor Model

Each **actor** is an isolated unit with its own state that communicates via **messages**. No shared state, no locks.

```
┌──────────────┐     message     ┌──────────────┐
│   Actor A     │ ──────────────→│   Actor B     │
│ ┌──────────┐ │                │ ┌──────────┐ │
│ │ Mailbox  │ │     message    │ │ Mailbox  │ │
│ │ [msg1]   │ │ ←──────────────│ │ [msg2]   │ │
│ │ [msg2]   │ │                │ │          │ │
│ └──────────┘ │                │ └──────────┘ │
│ State: {...}  │                │ State: {...}  │
│ (private)    │                │ (private)    │
└──────────────┘                └──────────────┘

Rules:
  1. Each actor has a mailbox (queue of incoming messages)
  2. Actor processes ONE message at a time (sequential)
  3. In response to a message, an actor can:
     - Send messages to other actors
     - Create new actors
     - Change its own state
  4. NO shared state → NO locks → NO race conditions!
```

```python
import asyncio
from dataclasses import dataclass
from typing import Any

@dataclass
class Message:
    type: str
    data: Any
    reply_to: asyncio.Queue = None

class Actor:
    def __init__(self, name):
        self.name = name
        self.mailbox = asyncio.Queue()
        self._task = None
    
    async def start(self):
        self._task = asyncio.create_task(self._run())
    
    async def _run(self):
        while True:
            msg = await self.mailbox.get()
            if msg.type == "STOP":
                break
            await self.handle(msg)
    
    async def handle(self, msg):
        raise NotImplementedError
    
    async def send(self, msg):
        await self.mailbox.put(msg)

class CounterActor(Actor):
    def __init__(self, name):
        super().__init__(name)
        self.count = 0
    
    async def handle(self, msg):
        if msg.type == "INCREMENT":
            self.count += msg.data
        elif msg.type == "GET":
            await msg.reply_to.put(self.count)

async def main():
    counter = CounterActor("counter")
    await counter.start()
    
    # Send messages (no shared state, no locks!)
    for _ in range(1000):
        await counter.send(Message("INCREMENT", 1))
    
    # Get result
    reply = asyncio.Queue()
    await counter.send(Message("GET", None, reply_to=reply))
    result = await reply.get()
    print(f"Count: {result}")  # 1000 ✅
    
    await counter.send(Message("STOP", None))

asyncio.run(main())
```

**Actor model is used by:** Erlang/OTP, Akka (Java/Scala), Elixir, Microsoft Orleans.

---

## CSP (Communicating Sequential Processes)

Similar to actors, but emphasizes **channels** instead of mailboxes. Processes communicate by sending values through channels.

```
Go uses CSP natively:
  ch := make(chan int)
  go producer(ch)     // goroutine sends to channel
  value := <-ch       // receive from channel

Python equivalent (using asyncio.Queue as channels):
```

```python
import asyncio

async def csp_producer(channel):
    for i in range(10):
        await channel.put(i)
        await asyncio.sleep(0.1)
    await channel.put(None)

async def csp_consumer(channel):
    while True:
        value = await channel.get()
        if value is None:
            break
        print(f"Received: {value}")

async def main():
    channel = asyncio.Queue()  # unbuffered channel equivalent
    await asyncio.gather(
        csp_producer(channel),
        csp_consumer(channel),
    )

asyncio.run(main())
```

### Actor Model vs CSP

| Aspect | Actor Model | CSP |
|--------|------------|-----|
| Communication | Direct (send to actor's mailbox) | Via channels (named pipes) |
| Identity | Actors have identifiers | Processes are anonymous |
| Coupling | Send knows receiver | Send knows channel, not receiver |
| Language | Erlang, Akka | Go, Clojure |

---

## Reactor Pattern

Event-driven pattern for handling **service requests** that arrive concurrently. A single event loop dispatches events to handlers.

```
                 ┌──────────────────────┐
  Event Source →  │  Event Demultiplexer  │  (select/epoll/kqueue)
  Event Source →  │  (single thread)      │
  Event Source →  │                      │
                 └──────────┬───────────┘
                            │ dispatch
              ┌─────────────┼────────────┐
              ▼             ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Handler A│ │ Handler B│ │ Handler C│
        └──────────┘ └──────────┘ └──────────┘

This is exactly how asyncio works!
  - Event loop = reactor
  - Coroutines = handlers
  - select/epoll = event demultiplexer
```

Used by: Node.js, Python asyncio, Nginx, Redis (single-threaded), Netty.

---

## Comparison: When to Use Which Pattern?

| Pattern | Use Case | Python Implementation |
|---------|----------|----------------------|
| **Producer-Consumer** | Task queue, buffer between stages | `queue.Queue`, `asyncio.Queue` |
| **Worker Pool** | Process N tasks with M workers | `ThreadPoolExecutor`, `ProcessPoolExecutor` |
| **Fan-Out/Fan-In** | Parallel processing + merge | `asyncio.gather`, `concurrent.futures` |
| **Pipeline** | Multi-stage data processing | Queues connecting stages |
| **Actor Model** | Isolated stateful agents | Custom (asyncio), Thespian, Ray |
| **CSP** | Channel-based communication | `asyncio.Queue` as channels |
| **Reactor** | I/O multiplexing, event handling | `asyncio` event loop |

---

## Interview Questions — Patterns

### Q1: Explain the Producer-Consumer pattern. When would you use it?

Producers generate items and put them in a shared buffer. Consumers take items from the buffer and process them. The buffer decouples production rate from consumption rate.

**Use cases:** Task queues (Celery), message brokers (Kafka → consumer groups), ETL pipelines, download managers.

### Q2: What is the Actor model? How does it avoid locks?

Each actor has its own **private state** and a **mailbox**. Actors communicate only by sending messages. Since state is never shared, there are no race conditions and no locks needed. Each actor processes messages sequentially from its mailbox.

### Q3: What patterns does Python's asyncio implement?

- **Reactor pattern:** The event loop IS a reactor — single-threaded event demultiplexer dispatching to coroutine handlers
- **Producer-Consumer:** `asyncio.Queue`
- **Fan-out/Fan-in:** `asyncio.gather()` or `TaskGroup`
