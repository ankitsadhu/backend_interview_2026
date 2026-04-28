# Redis Distributed Patterns & Real-World Use Cases

## 1. Distributed Locks (Redlock)

### Simple Lock (Single Instance)

```python
import redis
import uuid
import time

r = redis.Redis()

def acquire_lock(lock_name, timeout=10):
    """Acquire a distributed lock."""
    lock_id = str(uuid.uuid4())
    
    # SET NX EX — atomic "set if not exists" with expiry
    if r.set(f"lock:{lock_name}", lock_id, nx=True, ex=timeout):
        return lock_id
    return None

def release_lock(lock_name, lock_id):
    """Release lock ONLY if we own it (Lua for atomicity)."""
    script = """
    if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
    else
        return 0
    end
    """
    return r.eval(script, 1, f"lock:{lock_name}", lock_id)

# Usage
lock_id = acquire_lock("order:12345")
if lock_id:
    try:
        process_order(12345)
    finally:
        release_lock("order:12345", lock_id)
```

> ⚠️ **Why Lua for release?** Without it, there's a race condition:
> 1. Client A checks key → it's theirs
> 2. Key expires (TTL)
> 3. Client B acquires lock
> 4. Client A deletes key (deleting B's lock!)

### Redlock Algorithm (Multi-Instance)

For fault tolerance, acquire locks on **N independent Redis instances** (usually 5).

```
Step 1: Get current time T1
Step 2: Try to acquire lock on all N instances (with small timeout)
Step 3: Get current time T2
Step 4: Lock acquired if:
   - Majority (N/2 + 1) instances locked successfully
   - Total elapsed time (T2-T1) < lock TTL
Step 5: Effective TTL = original TTL - elapsed time
Step 6: If lock fails, release on ALL instances

┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
│Redis1│  │Redis2│  │Redis3│  │Redis4│  │Redis5│
│  ✅  │  │  ✅  │  │  ✅  │  │  ❌  │  │  ❌  │
└──────┘  └──────┘  └──────┘  └──────┘  └──────┘
Lock acquired! (3/5 = majority)
```

```python
# Using python-redis-lock or redlock-py
from redis.lock import Lock

lock = Lock(r, "resource:lock", timeout=10, blocking_timeout=5)

if lock.acquire():
    try:
        do_exclusive_work()
    finally:
        lock.release()

# Or as context manager
with Lock(r, "resource:lock", timeout=10):
    do_exclusive_work()
```

---

## 2. Rate Limiting Patterns

### Fixed Window Counter

```python
def is_rate_limited_fixed(user_id, limit=100, window=60):
    """Simple: count requests per window."""
    key = f"ratelimit:{user_id}:{int(time.time()) // window}"
    
    current = r.incr(key)
    if current == 1:
        r.expire(key, window)
    
    return current > limit
```

**Problem:** Boundary spikes — 100 requests at end of window + 100 at start of next = 200 in 1 second.

### Sliding Window Log

```python
def is_rate_limited_sliding(user_id, limit=100, window=60):
    """Precise: track each request timestamp."""
    key = f"ratelimit:{user_id}"
    now = time.time()
    
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)  # Remove old entries
    pipe.zadd(key, {str(now): now})              # Add current request
    pipe.zcard(key)                               # Count entries
    pipe.expire(key, window)                      # Set TTL
    _, _, count, _ = pipe.execute()
    
    return count > limit
```

### Token Bucket

```python
def token_bucket(user_id, capacity=10, refill_rate=1):
    """Token bucket: allows bursts up to capacity."""
    key = f"bucket:{user_id}"
    now = time.time()
    
    script = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    
    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(bucket[1]) or capacity
    local last_refill = tonumber(bucket[2]) or now
    
    -- Refill tokens based on elapsed time
    local elapsed = now - last_refill
    tokens = math.min(capacity, tokens + elapsed * refill_rate)
    
    if tokens >= 1 then
        tokens = tokens - 1
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)
        return 1  -- Allowed
    else
        redis.call('HSET', key, 'last_refill', now)
        return 0  -- Rate limited
    end
    """
    return r.eval(script, 1, key, capacity, refill_rate, now)
```

---

## 3. Session Management

```python
import json
import secrets

class RedisSessionStore:
    def __init__(self, redis_client, prefix="session:", ttl=3600):
        self.r = redis_client
        self.prefix = prefix
        self.ttl = ttl
    
    def create_session(self, user_id, data=None):
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id,
            "created_at": time.time(),
            **(data or {})
        }
        key = f"{self.prefix}{session_id}"
        self.r.setex(key, self.ttl, json.dumps(session_data))
        return session_id
    
    def get_session(self, session_id):
        key = f"{self.prefix}{session_id}"
        data = self.r.get(key)
        if data:
            self.r.expire(key, self.ttl)  # Refresh TTL on access
            return json.loads(data)
        return None
    
    def destroy_session(self, session_id):
        self.r.delete(f"{self.prefix}{session_id}")
    
    def destroy_all_user_sessions(self, user_id):
        """Invalidate all sessions for a user (e.g., password change)."""
        # Track sessions in a set
        session_ids = self.r.smembers(f"user_sessions:{user_id}")
        if session_ids:
            keys = [f"{self.prefix}{sid.decode()}" for sid in session_ids]
            self.r.delete(*keys)
            self.r.delete(f"user_sessions:{user_id}")
```

---

## 4. Leaderboard System

```python
class Leaderboard:
    def __init__(self, redis_client, name="leaderboard"):
        self.r = redis_client
        self.key = f"lb:{name}"
    
    def add_score(self, player_id, score):
        """Add or update player's score."""
        self.r.zadd(self.key, {player_id: score})
    
    def increment_score(self, player_id, delta):
        """Atomically increment score."""
        return self.r.zincrby(self.key, delta, player_id)
    
    def get_rank(self, player_id):
        """Get player's rank (0 = highest score)."""
        rank = self.r.zrevrank(self.key, player_id)
        return rank + 1 if rank is not None else None
    
    def get_top(self, n=10):
        """Get top N players."""
        return self.r.zrevrange(self.key, 0, n - 1, withscores=True)
    
    def get_around(self, player_id, range_size=5):
        """Get players around a specific player."""
        rank = self.r.zrevrank(self.key, player_id)
        if rank is None:
            return []
        start = max(0, rank - range_size)
        end = rank + range_size
        return self.r.zrevrange(self.key, start, end, withscores=True)
    
    def get_page(self, page=1, page_size=20):
        """Paginated leaderboard."""
        start = (page - 1) * page_size
        end = start + page_size - 1
        return self.r.zrevrange(self.key, start, end, withscores=True)
```

---

## 5. Job/Task Queue

```python
import json
import time
import uuid

class RedisQueue:
    def __init__(self, redis_client, queue_name="jobs"):
        self.r = redis_client
        self.queue = f"queue:{queue_name}"
        self.processing = f"queue:{queue_name}:processing"
        self.failed = f"queue:{queue_name}:failed"
    
    def enqueue(self, task_type, payload, priority=0):
        """Add job to queue. Higher priority = processed first."""
        job = {
            "id": str(uuid.uuid4()),
            "type": task_type,
            "payload": payload,
            "created_at": time.time(),
            "retries": 0
        }
        # Use sorted set for priority queue
        self.r.zadd(self.queue, {json.dumps(job): priority})
        return job["id"]
    
    def dequeue(self, timeout=30):
        """Get highest priority job (blocking)."""
        # Atomic: pop highest score from sorted set
        result = self.r.bzpopmax(self.queue, timeout=timeout)
        if result:
            _, job_data, score = result
            job = json.loads(job_data)
            # Track in processing set
            self.r.hset(self.processing, job["id"], job_data)
            return job
        return None
    
    def complete(self, job_id):
        """Mark job as completed."""
        self.r.hdel(self.processing, job_id)
    
    def fail(self, job_id, error, max_retries=3):
        """Handle job failure with retries."""
        job_data = self.r.hget(self.processing, job_id)
        if job_data:
            job = json.loads(job_data)
            job["retries"] += 1
            job["last_error"] = str(error)
            
            if job["retries"] < max_retries:
                # Re-enqueue with lower priority
                self.r.zadd(self.queue, {json.dumps(job): -job["retries"]})
            else:
                # Move to dead letter queue
                self.r.lpush(self.failed, json.dumps(job))
            
            self.r.hdel(self.processing, job_id)
```

---

## 6. Real-Time Analytics

```python
class RealTimeAnalytics:
    def __init__(self, redis_client):
        self.r = redis_client
    
    def track_page_view(self, page, user_id=None):
        """Track page views with multiple dimensions."""
        today = time.strftime("%Y-%m-%d")
        hour = time.strftime("%Y-%m-%d:%H")
        
        pipe = self.r.pipeline()
        
        # Total page views (counter)
        pipe.incr(f"pv:{page}:{today}")
        pipe.incr(f"pv:{page}:{hour}")
        
        # Unique visitors (HyperLogLog — 12KB per counter!)
        pipe.pfadd(f"uv:{page}:{today}", user_id or "anon")
        
        # Active users (bitmap)
        if user_id and user_id.isdigit():
            pipe.setbit(f"active:{today}", int(user_id), 1)
        
        # Popular pages (sorted set)
        pipe.zincrby(f"popular:{today}", 1, page)
        
        # Set TTL on all keys (7 days)
        for key in [f"pv:{page}:{today}", f"uv:{page}:{today}",
                     f"active:{today}", f"popular:{today}"]:
            pipe.expire(key, 86400 * 7)
        
        pipe.execute()
    
    def get_stats(self, page, date=None):
        date = date or time.strftime("%Y-%m-%d")
        return {
            "page_views": int(self.r.get(f"pv:{page}:{date}") or 0),
            "unique_visitors": self.r.pfcount(f"uv:{page}:{date}"),
            "rank": self.r.zrevrank(f"popular:{date}", page),
        }
    
    def get_dau(self, date=None):
        """Daily Active Users count."""
        date = date or time.strftime("%Y-%m-%d")
        return self.r.bitcount(f"active:{date}")
```

---

## Interview Questions — Distributed Patterns

### Q1: Design a URL shortener using Redis.

**Answer:**

```python
class URLShortener:
    def __init__(self, redis_client):
        self.r = redis_client
        self.COUNTER_KEY = "url:counter"
        self.CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    def _encode(self, num):
        """Convert number to base-62 string."""
        result = []
        while num > 0:
            result.append(self.CHARS[num % 62])
            num //= 62
        return ''.join(reversed(result)) or self.CHARS[0]
    
    def shorten(self, long_url):
        # Check if URL already shortened
        existing = self.r.hget("url:long_to_short", long_url)
        if existing:
            return existing.decode()
        
        # Generate short code
        counter = self.r.incr(self.COUNTER_KEY)
        short_code = self._encode(counter)
        
        # Store both directions
        pipe = self.r.pipeline()
        pipe.hset("url:short_to_long", short_code, long_url)
        pipe.hset("url:long_to_short", long_url, short_code)
        pipe.execute()
        
        return short_code
    
    def resolve(self, short_code):
        # Get long URL + track click
        long_url = self.r.hget("url:short_to_long", short_code)
        if long_url:
            self.r.hincrby("url:clicks", short_code, 1)
            return long_url.decode()
        return None
```

---

### Q2: How would you implement a "trending topics" feature using Redis?

**Answer:**

Use **Sorted Sets** with time-decayed scoring:

```python
def track_topic(topic, weight=1):
    """Score = sum of time-decayed weights."""
    now = time.time()
    
    # Sliding window: only keep last 24 hours
    pipe = r.pipeline()
    pipe.zremrangebyscore("trending", 0, now - 86400)
    
    # Each mention adds a score of (weight / age_factor)
    # Using current timestamp as score for recency
    pipe.zincrby("trending:scores", weight, topic)
    pipe.zadd("trending:last_seen", {topic: now})
    pipe.expire("trending:scores", 86400)
    pipe.execute()

def get_trending(n=10):
    """Get top N trending topics."""
    return r.zrevrange("trending:scores", 0, n - 1, withscores=True)

# Better approach: time-windowed counters
def track_trending_windowed(topic):
    """Count per-minute, aggregate for trending."""
    minute_key = f"trending:{int(time.time()) // 60}"
    r.zincrby(minute_key, 1, topic)
    r.expire(minute_key, 3600)  # Keep 1 hour of windows

def get_trending_windowed(n=10, windows=60):
    """Aggregate last N minutes."""
    now = int(time.time()) // 60
    keys = [f"trending:{now - i}" for i in range(windows)]
    
    # ZUNIONSTORE aggregates scores across all windows
    r.zunionstore("trending:result", keys)
    return r.zrevrange("trending:result", 0, n - 1, withscores=True)
```

---

### Q3: Design a distributed rate limiter for an API gateway serving 10M requests/sec across 50 servers.

**Answer:**

**Challenge:** Can't hit Redis for every request at 10M req/sec.

**Solution: Local + Global hybrid approach**

```
Each server:
┌──────────────────────────────────┐
│  Local token bucket              │
│  (in-memory, no Redis calls)     │
│  Capacity: global_limit / 50     │
│                                  │
│  Every 1 second:                 │
│    Sync with Redis               │
│    Adjust local limit based on   │
│    global usage                  │
└──────────────────────────────────┘
         │ (periodic sync)
         ▼
┌──────────────────────────────────┐
│  Redis (global state)            │
│  Key: ratelimit:{client_id}      │
│  Type: Sorted Set or Counter     │
└──────────────────────────────────┘
```

```python
class DistributedRateLimiter:
    def __init__(self, redis_client, total_servers=50):
        self.r = redis_client
        self.total_servers = total_servers
        self.local_tokens = {}
        self.sync_interval = 1  # seconds
    
    def check_local(self, client_id, limit_per_sec):
        """Fast local check (no Redis call)."""
        local_limit = limit_per_sec // self.total_servers
        
        key = f"{client_id}:{int(time.time())}"
        self.local_tokens[key] = self.local_tokens.get(key, 0) + 1
        
        return self.local_tokens[key] <= local_limit
    
    def sync_global(self, client_id, limit_per_sec):
        """Periodic sync with Redis (runs every second)."""
        window = int(time.time())
        key = f"{client_id}:{window}"
        local_count = self.local_tokens.get(key, 0)
        
        # Report local count to global
        global_count = self.r.incrby(f"rl:{client_id}:{window}", local_count)
        self.r.expire(f"rl:{client_id}:{window}", 5)
        
        # Adjust local limit based on global usage
        remaining_global = limit_per_sec - global_count
        remaining_servers = self.total_servers  # Approximate
        return max(0, remaining_global // remaining_servers)
```

Key design decisions:
- **99% of requests** checked locally (no Redis call)
- **1% sync frequency** to Redis for global coordination
- Allows slight over-limit (acceptable trade-off for throughput)
- Use Lua script for atomic Redis operations during sync
