# Redis Fundamentals

## What is Redis?

**Redis** = **RE**mote **DI**ctionary **S**erver

Redis is an **open-source, in-memory data structure store** used as a database, cache, message broker, and streaming engine.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **In-Memory** | All data lives in RAM → microsecond latency |
| **Single-Threaded** | One thread for command execution → no race conditions |
| **Persistence** | Optional durability via RDB snapshots + AOF logs |
| **Replication** | Master-replica architecture for high availability |
| **Rich Data Structures** | Not just key-value — supports lists, sets, sorted sets, hashes, streams, etc. |
| **Atomic Operations** | Every command is atomic; multi-command transactions via `MULTI/EXEC` |

---

## How Redis Works Internally

```
Client Request
     │
     ▼
┌──────────────────┐
│   Event Loop      │  ← Single-threaded (epoll/kqueue)
│   (I/O Multiplexing) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Command Parser   │  ← Parses RESP protocol
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Command Executor │  ← Executes against in-memory data structures
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Response Builder │  ← Sends response back via RESP
└──────────────────┘
```

### Why Single-Threaded?

- No context switching overhead
- No locks, no mutexes, no deadlocks
- Memory access is the bottleneck, not CPU
- Can handle **100,000+ ops/sec** on a single core
- I/O multiplexing (epoll) handles thousands of concurrent connections

> **Note:** Since Redis 6.0, I/O threads handle network reads/writes in parallel, but **command execution remains single-threaded**.

---

## Installation & Basic Usage

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install redis-server

# macOS
brew install redis

# Docker (recommended)
docker run -d --name redis -p 6379:6379 redis:latest

# Connect
redis-cli
```

### RESP Protocol (Redis Serialization Protocol)

Redis uses a simple text-based protocol:

```
*3\r\n       → Array of 3 elements
$3\r\n       → Bulk string of 3 bytes
SET\r\n      → "SET"
$5\r\n       → Bulk string of 5 bytes
mykey\r\n    → "mykey"
$7\r\n       → Bulk string of 7 bytes
myvalue\r\n  → "myvalue"
```

---

## Core Data Types

### 1. Strings

The most basic type. Can hold text, integers, floats, or binary data (max 512 MB).

```redis
SET name "Redis"            -- Set a key
GET name                     -- "Redis"
SET counter 10               -- Numeric string
INCR counter                 -- 11 (atomic increment)
DECR counter                 -- 10
INCRBY counter 5             -- 15
DECRBY counter 3             -- 12
INCRBYFLOAT price 2.5        -- Float increment

APPEND name " Rocks"         -- "Redis Rocks"
STRLEN name                  -- 11

MSET a 1 b 2 c 3            -- Set multiple keys
MGET a b c                   -- ["1", "2", "3"]

SETNX key "value"            -- Set only if NOT exists (returns 0 if exists)
SET key "value" EX 60        -- Set with 60-second TTL
SET key "value" PX 5000      -- Set with 5000ms TTL
SET key "value" NX EX 30     -- Distributed lock pattern!

GETSET key "new"             -- Returns old value, sets new (atomic)
GETDEL key                   -- Get and delete (Redis 6.2+)
```

**Use Cases:** Caching, counters, rate limiters, session tokens, distributed locks

---

### 2. Lists (Linked Lists)

Ordered collection of strings. Implemented as **quicklists** (linked list of ziplists).

```redis
LPUSH tasks "task1"          -- Push left  → [task1]
RPUSH tasks "task2"          -- Push right → [task1, task2]
LPUSH tasks "task0"          -- [task0, task1, task2]

LRANGE tasks 0 -1            -- Get all: [task0, task1, task2]
LRANGE tasks 0 1             -- [task0, task1]

LPOP tasks                   -- Remove & return left: "task0"
RPOP tasks                   -- Remove & return right: "task2"

LLEN tasks                   -- Length
LINDEX tasks 0               -- Element at index 0
LSET tasks 0 "updated"       -- Set element at index

LINSERT tasks BEFORE "task1" "task0.5"  -- Insert before element

-- Blocking operations (great for queues!)
BLPOP queue 30               -- Block for 30s until element available
BRPOP queue 30
BRPOPLPUSH source dest 30    -- Atomic pop from source, push to dest
```

**Use Cases:** Message queues, activity feeds, task queues, recent items list

---

### 3. Sets (Unordered, Unique)

Unordered collection of unique strings. Implemented as **hash tables**.

```redis
SADD fruits "apple" "banana" "cherry"
SMEMBERS fruits              -- {"apple", "banana", "cherry"}
SCARD fruits                 -- 3 (cardinality)

SISMEMBER fruits "apple"     -- 1 (true)
SISMEMBER fruits "grape"     -- 0 (false)

SREM fruits "banana"         -- Remove member
SPOP fruits                  -- Remove & return random member
SRANDMEMBER fruits 2         -- Return 2 random members (no removal)

-- Set operations
SADD setA "a" "b" "c"
SADD setB "b" "c" "d"

SUNION setA setB             -- {"a", "b", "c", "d"}
SINTER setA setB             -- {"b", "c"}
SDIFF setA setB              -- {"a"} (in A but not B)

SUNIONSTORE destKey setA setB  -- Store result in destKey
```

**Use Cases:** Tags, unique visitors, mutual friends, voting systems

---

### 4. Sorted Sets (ZSets)

Like sets, but each member has a **score** (float). Ordered by score. Implemented as **skip lists + hash tables**.

```redis
ZADD leaderboard 100 "alice"
ZADD leaderboard 200 "bob"
ZADD leaderboard 150 "charlie"

ZRANGE leaderboard 0 -1              -- By rank ascending: [alice, charlie, bob]
ZRANGE leaderboard 0 -1 WITHSCORES   -- With scores
ZREVRANGE leaderboard 0 -1           -- Descending: [bob, charlie, alice]

ZRANK leaderboard "bob"              -- 2 (0-indexed rank)
ZREVRANK leaderboard "bob"           -- 0 (highest rank)
ZSCORE leaderboard "bob"             -- "200"

ZINCRBY leaderboard 50 "alice"       -- alice score = 150

ZRANGEBYSCORE leaderboard 100 200    -- Members with score 100-200
ZRANGEBYSCORE leaderboard -inf +inf  -- All members by score
ZRANGEBYSCORE leaderboard 100 200 LIMIT 0 10  -- With pagination

ZCOUNT leaderboard 100 200           -- Count members with score in range
ZCARD leaderboard                    -- Total members

ZREM leaderboard "charlie"           -- Remove member
ZREMRANGEBYSCORE leaderboard 0 100   -- Remove by score range
ZREMRANGEBYRANK leaderboard 0 1      -- Remove by rank range
```

**Use Cases:** Leaderboards, priority queues, rate limiting (sliding window), time-series indexes

---

### 5. Hashes

Field-value pairs within a single key. Like a mini key-value store per key.

```redis
HSET user:1001 name "Alice" age "30" email "alice@example.com"

HGET user:1001 name              -- "Alice"
HGETALL user:1001                -- {name: Alice, age: 30, email: alice@example.com}
HMGET user:1001 name age         -- ["Alice", "30"]

HSET user:1001 city "NYC"        -- Add/update field
HDEL user:1001 email             -- Delete field

HEXISTS user:1001 name           -- 1 (true)
HKEYS user:1001                  -- [name, age, city]
HVALS user:1001                  -- [Alice, 30, NYC]
HLEN user:1001                   -- 3

HINCRBY user:1001 age 1          -- Increment numeric field
HINCRBYFLOAT user:1001 score 0.5
```

**Use Cases:** User profiles, product details, configuration, session data, object storage

---

### 6. Bitmaps

Strings treated as bit arrays. Extremely memory-efficient for boolean data.

```redis
SETBIT daily_active:2026-03-16 1001 1    -- User 1001 was active
SETBIT daily_active:2026-03-16 1002 1

GETBIT daily_active:2026-03-16 1001      -- 1 (active)
GETBIT daily_active:2026-03-16 9999      -- 0 (not active)

BITCOUNT daily_active:2026-03-16         -- Count of active users

-- Bitwise operations across days
BITOP AND weekly_active day1 day2 day3 day4 day5 day6 day7
BITCOUNT weekly_active                   -- Users active ALL 7 days

BITOP OR any_day_active day1 day2 day3
BITCOUNT any_day_active                  -- Users active ANY day
```

**Use Cases:** Daily active users, feature flags, bloom filters, real-time analytics

---

### 7. HyperLogLog

Probabilistic data structure for **cardinality estimation** with 0.81% standard error. Uses only **12 KB** regardless of element count.

```redis
PFADD unique_visitors "user1" "user2" "user3"
PFADD unique_visitors "user1"          -- Duplicate, not counted

PFCOUNT unique_visitors                -- ~3

-- Merge multiple HLLs
PFADD page1_visitors "user1" "user2"
PFADD page2_visitors "user2" "user3"
PFMERGE all_visitors page1_visitors page2_visitors
PFCOUNT all_visitors                   -- ~3
```

**Use Cases:** Unique visitor counting, unique search queries, distinct event counting

---

### 8. Streams (Redis 5.0+)

Append-only log data structure (like Kafka topics).

```redis
-- Add entries
XADD mystream * sensor-id 1234 temperature 19.8
XADD mystream * sensor-id 1234 temperature 20.1
-- * = auto-generate ID (timestamp-sequence)

-- Read entries
XLEN mystream                          -- Count entries
XRANGE mystream - +                    -- All entries (- = min, + = max)
XRANGE mystream - + COUNT 10           -- First 10

-- Consumer groups (like Kafka consumer groups)
XGROUP CREATE mystream mygroup 0       -- Create group starting from beginning
XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS mystream >
-- > = only new messages not yet delivered

XACK mystream mygroup 1526569495631-0  -- Acknowledge processing
XPENDING mystream mygroup              -- Check pending (unacknowledged) messages
```

**Use Cases:** Event sourcing, activity streams, IoT data ingestion, message queues with acknowledgment

---

## Key Expiration & TTL

```redis
SET session:abc123 "user_data" EX 3600   -- Expire in 1 hour

TTL session:abc123              -- Remaining seconds (-1 = no expiry, -2 = key doesn't exist)
PTTL session:abc123             -- Remaining milliseconds

EXPIRE key 300                  -- Set expiry on existing key (300s)
PEXPIRE key 5000                -- Set expiry in milliseconds
EXPIREAT key 1700000000         -- Expire at Unix timestamp
PERSIST key                     -- Remove expiry (make permanent)
```

### How Expiration Works Internally

Redis uses **two strategies**:

1. **Passive (Lazy) Expiration:** Key is checked on access — if expired, it's deleted and `nil` returned.
2. **Active Expiration:** Redis periodically (10 times/sec) samples 20 random keys with expiry. If >25% are expired, repeat immediately.

> This means expired keys may linger briefly in memory until accessed or sampled.

---

## Key Naming Conventions

```redis
-- Use colons as separators (convention, not enforced)
user:1001:profile
user:1001:session
order:2026-03-16:items
cache:api:v2:users:list

-- Avoid very long keys (wastes memory)
-- Avoid very short keys (unreadable)
-- Good: user:1001:email
-- Bad:  u:1001:e
-- Bad:  user_one_thousand_and_one_email_address
```

---

## Common Interview Questions — Beginner

### Q1: What is the difference between Redis and Memcached?

| Feature | Redis | Memcached |
|---------|-------|-----------|
| Data Types | Strings, Lists, Sets, Hashes, Sorted Sets, Streams, etc. | Strings only |
| Persistence | RDB + AOF | None |
| Replication | Built-in master-replica | None (client-side) |
| Pub/Sub | Built-in | None |
| Transactions | MULTI/EXEC | None |
| Lua Scripting | Yes | None |
| Max Value Size | 512 MB | 1 MB |
| Threading | Single-threaded (I/O threads in 6.0+) | Multi-threaded |
| Cluster Mode | Built-in | Client-side consistent hashing |

**When to use Memcached:** Simple caching of strings, multi-threaded performance needed, no persistence needed.
**When to use Redis:** Rich data structures, persistence, pub/sub, queues, complex caching patterns.

---

### Q2: Why is Redis so fast even though it's single-threaded?

1. **In-memory storage** — RAM access is ~100ns vs ~10ms for disk
2. **No context switching** — single thread, no thread synchronization
3. **I/O multiplexing** — epoll/kqueue handles thousands of connections efficiently
4. **Optimized data structures** — skip lists, hash tables, ziplists are cache-friendly
5. **Simple protocol (RESP)** — minimal parsing overhead
6. **No disk I/O in critical path** — persistence is async/background

---

### Q3: What happens when Redis runs out of memory?

Depends on the `maxmemory-policy` configuration:

| Policy | Behavior |
|--------|----------|
| `noeviction` | Returns error for write commands (default) |
| `allkeys-lru` | Evict least recently used keys |
| `allkeys-lfu` | Evict least frequently used keys |
| `volatile-lru` | LRU only among keys with TTL set |
| `volatile-lfu` | LFU only among keys with TTL set |
| `volatile-ttl` | Evict keys with shortest TTL |
| `allkeys-random` | Evict random keys |
| `volatile-random` | Random eviction among keys with TTL |

```redis
CONFIG SET maxmemory 256mb
CONFIG SET maxmemory-policy allkeys-lru
```

---

### Q4: Explain the difference between `SETNX` and `SET ... NX`.

Both set a key **only if it doesn't exist**, but:

```redis
SETNX mykey "value"             -- Old command, returns 1 (set) or 0 (not set)
SET mykey "value" NX EX 30      -- Modern: SET with NX flag + expiry (atomic!)
```

`SET ... NX EX` is preferred for **distributed locks** because it's atomic — you can't have a race between `SETNX` and `EXPIRE`.
