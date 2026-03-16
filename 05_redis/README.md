# Redis Study Guide

> Comprehensive Redis learning path from beginner to advanced, organized for interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | What is Redis, architecture, data types (Strings, Lists, Sets, Sorted Sets, Hashes, Bitmaps, HyperLogLog, Streams), key expiration, naming conventions | 🟢 Beginner |
| 02 | [Persistence](./02_persistence.md) | RDB snapshots, AOF logging, hybrid persistence, copy-on-write, persistence decision matrix | 🟢🟡 Beginner-Intermediate |
| 03 | [Caching Patterns](./03_caching_patterns.md) | Cache-aside, read-through, write-through, write-behind, write-around, cache invalidation, cache stampede prevention | 🟡 Intermediate |
| 04 | [Pub/Sub & Messaging](./04_pubsub_and_messaging.md) | Pub/Sub, Redis Streams, consumer groups, message queues with Lists, keyspace notifications | 🟡 Intermediate |
| 05 | [High Availability](./05_high_availability.md) | Replication, Redis Sentinel, Redis Cluster, hash slots, failover, split-brain prevention | 🟡🔴 Intermediate-Advanced |
| 06 | [Transactions & Scripting](./06_transactions_lua_pipelining.md) | MULTI/EXEC, WATCH (optimistic locking), Lua scripting, pipelining, rate limiter scripts | 🟡🔴 Intermediate-Advanced |
| 07 | [Distributed Patterns](./07_distributed_patterns.md) | Distributed locks (Redlock), rate limiting algorithms, session management, leaderboards, job queues, real-time analytics | 🔴 Advanced |
| 08 | [Performance & Production](./08_performance_and_production.md) | Memory optimization, command optimization, slow log, security, production config, monitoring | 🔴 Advanced |
| 09 | [Interview Questions](./09_interview_questions.md) | 20+ categorized questions (beginner → advanced) + rapid-fire Q&A + system design | 🟢🟡🔴 All Levels |

## 🎯 Study Path

### Week 1: Foundations
1. Read `01_fundamentals.md` — understand all data types and commands
2. Practice commands using `redis-cli` or [try.redis.io](https://try.redis.io)
3. Read `02_persistence.md` — understand RDB vs AOF trade-offs

### Week 2: Patterns & Architecture
4. Read `03_caching_patterns.md` — master cache-aside and invalidation strategies
5. Read `04_pubsub_and_messaging.md` — understand Pub/Sub vs Streams
6. Read `05_high_availability.md` — Sentinel vs Cluster decision matrix

### Week 3: Advanced & Production
7. Read `06_transactions_lua_pipelining.md` — write Lua scripts
8. Read `07_distributed_patterns.md` — implement locks, rate limiters
9. Read `08_performance_and_production.md` — production configuration

### Final Review
10. Go through `09_interview_questions.md` — test yourself across all levels
