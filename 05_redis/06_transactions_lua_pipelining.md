# Redis Transactions, Lua Scripting & Pipelining

## Transactions (MULTI/EXEC)

Redis transactions guarantee **atomic execution** of a group of commands.

### Basic Transaction

```redis
MULTI                           -- Start transaction
SET account:alice 1000
SET account:bob 500
DECRBY account:alice 200
INCRBY account:bob 200
EXEC                            -- Execute all commands atomically
-- Returns: [OK, OK, 800, 700]

DISCARD                         -- Abort transaction (instead of EXEC)
```

### Key Points

| Feature | Behavior |
|---------|----------|
| **Atomicity** | All commands execute sequentially, no interleaving |
| **Isolation** | No other client sees partial transaction state |
| **No Rollback** | If a command fails, others still execute! |
| **No Nested** | Cannot nest MULTI/EXEC |
| **Queued** | Commands are queued, not executed until EXEC |

> ⚠️ **Redis transactions are NOT like SQL transactions.** There's no rollback. If `INCRBY` fails (e.g., on a string), `DECRBY` still executes.

### WATCH (Optimistic Locking)

`WATCH` provides **check-and-set (CAS)** behavior — a form of optimistic locking.

```redis
WATCH account:alice             -- Watch for changes
GET account:alice               -- Read current value → "1000"

MULTI
DECRBY account:alice 200        -- Will only work if account:alice hasn't changed
INCRBY account:bob 200
EXEC
-- Returns: [800, 700] if no one modified account:alice
-- Returns: (nil) if someone else modified it → transaction aborted!
```

```python
# Python — transfer with optimistic locking
def transfer(from_acct, to_acct, amount):
    with r.pipeline() as pipe:
        while True:
            try:
                # Watch the source account
                pipe.watch(f"account:{from_acct}")
                
                balance = int(pipe.get(f"account:{from_acct}"))
                if balance < amount:
                    raise Exception("Insufficient funds")
                
                # Start transaction
                pipe.multi()
                pipe.decrby(f"account:{from_acct}", amount)
                pipe.incrby(f"account:{to_acct}", amount)
                pipe.execute()  # Atomic execution
                break  # Success
                
            except redis.WatchError:
                continue  # Retry — someone else modified the key
```

---

## Lua Scripting

Lua scripts execute **atomically** on the Redis server — no other command runs between script commands.

### Basic Scripts

```redis
-- Simple script
EVAL "return 'Hello, Redis!'" 0
-- 0 = number of KEYS arguments

-- Access KEYS and ARGV
EVAL "return redis.call('SET', KEYS[1], ARGV[1])" 1 mykey myvalue
-- 1 = one KEYS argument, KEYS[1]="mykey", ARGV[1]="myvalue"

-- Multi-command script
EVAL "
  local current = redis.call('GET', KEYS[1])
  if current == false then
    redis.call('SET', KEYS[1], ARGV[1])
    return 1
  else
    return 0
  end
" 1 mykey "default_value"
```

### Script Caching (EVALSHA)

```redis
-- Load script (returns SHA1 hash)
SCRIPT LOAD "return redis.call('GET', KEYS[1])"
-- Returns: "a42059b356c875f0717db19a51f6aaa9161571a2"

-- Execute by SHA1 (no need to send script text again)
EVALSHA "a42059b356c875f0717db19a51f6aaa9161571a2" 1 mykey

-- Check if script exists
SCRIPT EXISTS "a42059b356c875f0717db19a51f6aaa9161571a2"

-- Flush script cache
SCRIPT FLUSH
```

### Practical Lua Script Examples

#### Rate Limiter (Sliding Window)

```lua
-- KEYS[1] = rate limit key
-- ARGV[1] = window size in seconds
-- ARGV[2] = max requests
-- ARGV[3] = current timestamp

local key = KEYS[1]
local window = tonumber(ARGV[1])
local max_requests = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Remove entries outside the window
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

-- Count current requests
local current = redis.call('ZCARD', key)

if current < max_requests then
    -- Allow request
    redis.call('ZADD', key, now, now .. math.random())
    redis.call('EXPIRE', key, window)
    return 1  -- Allowed
else
    return 0  -- Rate limited
end
```

```python
# Python usage
rate_limit_script = r.register_script("""
    local key = KEYS[1]
    local window = tonumber(ARGV[1])
    local max_requests = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
    local current = redis.call('ZCARD', key)
    if current < max_requests then
        redis.call('ZADD', key, now, now .. math.random())
        redis.call('EXPIRE', key, window)
        return 1
    else
        return 0
    end
""")

# Check: max 100 requests per 60 seconds for user 1001
import time
allowed = rate_limit_script(
    keys=["ratelimit:user:1001"],
    args=[60, 100, int(time.time())]
)
```

#### Atomic Compare-and-Swap

```lua
-- Only update if current value matches expected
-- KEYS[1] = key
-- ARGV[1] = expected current value
-- ARGV[2] = new value

local current = redis.call('GET', KEYS[1])
if current == ARGV[1] then
    redis.call('SET', KEYS[1], ARGV[2])
    return 1  -- Updated
else
    return 0  -- Value changed, not updated
end
```

#### Distributed Counter with Limit

```lua
-- Increment counter but cap at max value
-- KEYS[1] = counter key
-- ARGV[1] = max value
-- ARGV[2] = increment amount

local current = tonumber(redis.call('GET', KEYS[1]) or "0")
local max_val = tonumber(ARGV[1])
local incr = tonumber(ARGV[2])

if current + incr <= max_val then
    return redis.call('INCRBY', KEYS[1], incr)
else
    return -1  -- Would exceed limit
end
```

### Lua Scripting Rules

| Rule | Reason |
|------|--------|
| Scripts must be **deterministic** | Same inputs → same outputs (for replication) |
| No random, time, or OS calls | Use `redis.call('TIME')` instead |
| All keys must be in `KEYS[]` | Required for cluster slot routing |
| Max execution time: 5s default | `lua-time-limit 5000` (configurable) |
| `redis.call()` vs `redis.pcall()` | `call` raises error, `pcall` returns error as value |

---

## Pipelining

Send multiple commands **without waiting** for individual responses. Reduces round-trip latency.

### Without Pipeline (Slow)

```
Client          Redis
  │── SET a 1 ──→│
  │←── OK ───────│   Round trip 1
  │── SET b 2 ──→│
  │←── OK ───────│   Round trip 2
  │── SET c 3 ──→│
  │←── OK ───────│   Round trip 3
  Total: 3 round trips
```

### With Pipeline (Fast)

```
Client          Redis
  │── SET a 1 ──→│
  │── SET b 2 ──→│
  │── SET c 3 ──→│   All sent at once
  │←── OK ───────│
  │←── OK ───────│   All responses returned together
  │←── OK ───────│
  Total: 1 round trip
```

### Python Pipeline

```python
# Without pipeline: 1000 round trips
for i in range(1000):
    r.set(f"key:{i}", f"value:{i}")  # ~1000 * 0.5ms = 500ms

# With pipeline: 1 round trip
pipe = r.pipeline()
for i in range(1000):
    pipe.set(f"key:{i}", f"value:{i}")
results = pipe.execute()  # ~1ms total!

# Pipeline with transaction (MULTI/EXEC)
pipe = r.pipeline(transaction=True)  # default
pipe.set("a", 1)
pipe.set("b", 2)
pipe.execute()  # Wrapped in MULTI/EXEC

# Pipeline WITHOUT transaction
pipe = r.pipeline(transaction=False)
pipe.set("a", 1)
pipe.set("b", 2)
pipe.execute()  # Just batched, no MULTI/EXEC
```

### Pipeline vs Transaction vs Lua

| Feature | Pipeline | Transaction (MULTI) | Lua Script |
|---------|----------|-------------------|------------|
| Reduces RTT | ✅ Yes | ✅ (when pipelined) | ✅ Yes |
| Atomic | ❌ No | ✅ Yes | ✅ Yes |
| Conditional Logic | ❌ No | ❌ No | ✅ Yes |
| Single network call | ✅ Yes | ✅ (with pipeline) | ✅ Yes |
| Server-side logic | ❌ No | ❌ No | ✅ Yes |
| Works in Cluster | ✅ (same slot) | ✅ (same slot) | ✅ (same slot) |

---

## Interview Questions — Transactions & Scripting

### Q1: Why doesn't Redis support rollback in transactions?

**Answer:**
Redis philosophy: **errors in transactions are programming bugs, not runtime failures.**

- Commands only fail if there's a **type mismatch** (e.g., `INCR` on a list) — which is a bug
- No support for constraint violations (no schema)
- Rollback would require **undo logs** → complexity + memory overhead
- Redis prioritizes **simplicity and performance**
- If you need complex transactions, use Lua scripts for conditional logic

---

### Q2: Write a Lua script to implement a leaky bucket rate limiter.

**Answer:**

```lua
-- KEYS[1] = bucket key
-- ARGV[1] = bucket capacity
-- ARGV[2] = leak rate (requests per second)
-- ARGV[3] = current timestamp (seconds)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local leak_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Get current bucket state
local bucket = redis.call('HMGET', key, 'water', 'last_leak')
local water = tonumber(bucket[1]) or 0
local last_leak = tonumber(bucket[2]) or now

-- Leak water based on time elapsed
local elapsed = now - last_leak
local leaked = elapsed * leak_rate
water = math.max(0, water - leaked)

-- Try to add one drop
if water < capacity then
    water = water + 1
    redis.call('HMSET', key, 'water', water, 'last_leak', now)
    redis.call('EXPIRE', key, math.ceil(capacity / leak_rate) + 1)
    return 1  -- Allowed
else
    redis.call('HSET', key, 'last_leak', now)
    return 0  -- Rate limited
end
```

---

### Q3: You need to increment a counter and check if it exceeds a threshold atomically. How?

**Answer:** Use a Lua script — `MULTI/EXEC` can't do conditional logic.

```lua
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], tonumber(ARGV[2]))  -- Set TTL on first increment
end
if count > tonumber(ARGV[1]) then
    return 0  -- Threshold exceeded
else
    return count  -- Current count (within limit)
end
```

```python
check_threshold = r.register_script("""
    local count = redis.call('INCR', KEYS[1])
    if count == 1 then
        redis.call('EXPIRE', KEYS[1], tonumber(ARGV[2]))
    end
    if count > tonumber(ARGV[1]) then
        return 0
    else
        return count
    end
""")

# Max 100 requests per 60-second window
result = check_threshold(keys=["counter:api:user:1001"], args=[100, 60])
if result == 0:
    print("Rate limited!")
```
