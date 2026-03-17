# Concurrency Study Guide

> Comprehensive concurrency learning path from fundamentals to advanced, with Python focus and interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | Concurrency vs parallelism, processes vs threads, GIL, race conditions, deadlocks, CPU-bound vs I/O-bound | 🟢 Beginner |
| 02 | [Threading](./02_threading.md) | Python `threading`, locks, RLock, semaphores, events, barriers, conditions, thread pools, `concurrent.futures` | 🟢🟡 Beginner-Intermediate |
| 03 | [Multiprocessing](./03_multiprocessing.md) | `multiprocessing`, Process, Pool, shared memory, IPC (Queue, Pipe), `ProcessPoolExecutor` | 🟡 Intermediate |
| 04 | [Asyncio](./04_asyncio.md) | Event loop, coroutines, `async`/`await`, tasks, `gather`, `aiohttp`, `asyncpg`, structured concurrency | 🟡 Intermediate |
| 05 | [Synchronization](./05_synchronization.md) | Mutex, semaphore, read-write lock, atomic operations, memory ordering, lock-free data structures | 🟡🔴 Intermediate-Advanced |
| 06 | [Concurrency Patterns](./06_concurrency_patterns.md) | Producer-consumer, worker pool, fan-out/fan-in, pipeline, actor model, CSP, reactor, proactor | 🔴 Advanced |
| 07 | [Interview Questions](./07_interview_questions.md) | 25+ questions (beginner → advanced) + rapid-fire Q&A + coding challenges | 🟢🟡🔴 All Levels |

## 🎯 Study Path

### Week 1: Foundations
1. Read `01_fundamentals.md` — understand concurrency vs parallelism, the GIL
2. Read `02_threading.md` — threading primitives and thread pools
3. Read `03_multiprocessing.md` — bypassing the GIL for CPU-bound work

### Week 2: Async & Synchronization
4. Read `04_asyncio.md` — master async/await for I/O-bound work
5. Read `05_synchronization.md` — deep dive into locks and atomics

### Week 3: Patterns & Interview Prep
6. Read `06_concurrency_patterns.md` — producer-consumer, pipelines, actors
7. Go through `07_interview_questions.md` — test yourself

## 📚 Recommended Reading

- *Python Concurrency with asyncio* — Matthew Fowler
- *Fluent Python, Ch. 19-21* — Luciano Ramalho
- *The Art of Multiprocessor Programming* — Herlihy & Shavit
