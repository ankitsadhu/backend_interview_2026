# Redis Caching Patterns & Strategies

## Caching Patterns Overview

```
┌───────────────────────────────────────────────────┐
│                Caching Patterns                    │
├──────────────┬──────────────┬─────────────────────┤
│  Read        │  Write       │  Eviction            │
├──────────────┼──────────────┼─────────────────────┤
│ Cache-Aside  │ Write-Through│ LRU / LFU            │
│ Read-Through │ Write-Behind │ TTL-Based             │
│              │ Write-Around │ Manual Invalidation   │
└──────────────┴──────────────┴─────────────────────┘
```

---

## 1. Cache-Aside (Lazy Loading)

The **most common** pattern. Application manages both cache and database.

```
Read Flow:
┌────────┐    1. GET key     ┌────────┐
│  App   │ ───────────────→  │ Redis  │
│        │ ←───────────────  │        │
│        │    Cache HIT?     └────────┘
│        │       │
│        │    NO (Cache MISS)
│        │       │
│        │    2. Query DB    ┌────────┐
│        │ ───────────────→  │   DB   │
│        │ ←───────────────  │        │
│        │    3. SET in cache └────────┘
└────────┘
```

```python
import redis
import json

r = redis.Redis()

def get_user(user_id):
    # Step 1: Try cache
    cached = r.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)  # Cache HIT
    
    # Step 2: Cache MISS → query database
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    
    # Step 3: Populate cache with TTL
    r.setex(f"user:{user_id}", 3600, json.dumps(user))
    
    return user

def update_user(user_id, data):
    # Update database
    db.execute("UPDATE users SET ... WHERE id = %s", user_id, data)
    
    # Invalidate cache (delete, don't update!)
    r.delete(f"user:{user_id}")
```

| ✅ Pros | ❌ Cons |
|---------|---------|
| Simple, widely understood | Cache miss → slow first request |
| Only caches what's needed | Stale data between invalidation |
| App controls caching logic | Two round-trips on miss |

---

## 2. Read-Through

Cache sits **between** app and DB. Cache itself fetches from DB on miss.

```
┌────────┐    GET key    ┌─────────────┐    Query DB    ┌────────┐
│  App   │ ──────────→   │ Cache Layer │ ────────────→  │   DB   │
│        │ ←──────────   │ (auto-loads) │ ←────────────  │        │
└────────┘               └─────────────┘                └────────┘
```

> **Note:** Redis doesn't natively support read-through. You implement it with a wrapper layer or use Redis Gears / custom module.

---

## 3. Write-Through

Every write goes to **both cache and DB** synchronously.

```python
def save_user(user_id, data):
    # Write to DB
    db.execute("INSERT INTO users ...", data)
    
    # Write to cache (synchronous)
    r.setex(f"user:{user_id}", 3600, json.dumps(data))
```

```
Write Flow:
┌────────┐   1. Write   ┌────────┐
│  App   │ ──────────→  │ Redis  │   (cache updated)
│        │              └────────┘
│        │   2. Write   ┌────────┐
│        │ ──────────→  │   DB   │   (DB updated)
└────────┘              └────────┘
```

| ✅ Pros | ❌ Cons |
|---------|---------|
| Cache always consistent with DB | Higher write latency (two writes) |
| No stale reads | Writes data that may never be read |
| Simple mental model | Two points of failure |

---

## 4. Write-Behind (Write-Back)

Write to cache immediately, **asynchronously** flush to DB in background.

```
┌────────┐   1. Write   ┌────────┐
│  App   │ ──────────→  │ Redis  │   (immediate response)
└────────┘              │        │
                        │ 2. Async│   ┌────────┐
                        │ batch  │──→│   DB   │  (batched writes)
                        └────────┘   └────────┘
```

```python
# Using a background worker
def save_user(user_id, data):
    # Write to cache only (fast!)
    r.setex(f"user:{user_id}", 3600, json.dumps(data))
    
    # Queue async DB write
    r.lpush("write_queue", json.dumps({"user_id": user_id, "data": data}))

# Background worker
def db_writer():
    while True:
        item = r.brpop("write_queue", timeout=5)
        if item:
            payload = json.loads(item[1])
            db.execute("UPSERT users ...", payload["data"])
```

| ✅ Pros | ❌ Cons |
|---------|---------|
| Very fast writes | Data loss risk if cache fails before DB write |
| Reduces DB load (batch writes) | Complex error handling |
| Great for high-throughput | Eventual consistency |

---

## 5. Write-Around

Write directly to DB, **skip cache**. Cache populated only on reads.

```python
def save_user(user_id, data):
    db.execute("INSERT INTO users ...", data)
    # Do NOT write to cache

def get_user(user_id):
    # Cache-aside pattern for reads
    cached = r.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    r.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

| ✅ Pros | ❌ Cons |
|---------|---------|
| Avoids caching rarely-read data | Cache miss after every write |
| Less cache churn | Higher read latency after writes |

---

## Cache Invalidation Strategies

> _"There are only two hard things in Computer Science: cache invalidation and naming things."_ — Phil Karlton

### 1. TTL-Based Expiration

```redis
SET key "value" EX 3600           -- Expire in 1 hour
```

- **Simplest approach** — data auto-expires
- Trade-off: shorter TTL = more DB hits, longer TTL = staler data

### 2. Event-Driven Invalidation

```python
# On DB update, publish invalidation event
def update_user(user_id, data):
    db.execute("UPDATE users ...", data)
    r.publish("cache:invalidate", f"user:{user_id}")

# Subscriber deletes the key
def invalidation_listener():
    pubsub = r.pubsub()
    pubsub.subscribe("cache:invalidate")
    for message in pubsub.listen():
        if message["type"] == "message":
            r.delete(message["data"])
```

### 3. Version-Based Invalidation

```python
# Increment version on update → old cache keys become orphaned
def get_user(user_id):
    version = r.get(f"user:{user_id}:version") or "1"
    cache_key = f"user:{user_id}:v{version}"
    
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    r.setex(cache_key, 3600, json.dumps(user))
    return user

def update_user(user_id, data):
    db.execute("UPDATE users ...", data)
    r.incr(f"user:{user_id}:version")  # Old version key becomes orphaned
```

---

## Cache Stampede (Thundering Herd)

**Problem:** When a popular cache key expires, hundreds of concurrent requests all miss the cache and hit the DB simultaneously.

### Solution 1: Distributed Lock

```python
def get_user_with_lock(user_id):
    cache_key = f"user:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    lock_key = f"lock:{cache_key}"
    # Only one request rebuilds cache
    if r.set(lock_key, "1", nx=True, ex=10):
        try:
            user = db.query("SELECT * FROM users WHERE id = %s", user_id)
            r.setex(cache_key, 3600, json.dumps(user))
            return user
        finally:
            r.delete(lock_key)
    else:
        # Others wait and retry
        import time
        time.sleep(0.1)
        return get_user_with_lock(user_id)
```

### Solution 2: Probabilistic Early Expiration

```python
import random, time

def get_with_early_refresh(key, ttl=3600, beta=1.0):
    cached, created_at = r.hmget(f"{key}:meta", "value", "created")
    
    if cached:
        age = time.time() - float(created_at)
        # Probabilistically refresh before TTL expires
        if age + beta * random.random() * 60 < ttl:
            return json.loads(cached)
    
    # Rebuild cache
    value = fetch_from_db(key)
    r.hmset(f"{key}:meta", {"value": json.dumps(value), "created": time.time()})
    r.expire(f"{key}:meta", ttl)
    return value
```

### Solution 3: Never Expire + Background Refresh

```python
# Set key with no TTL, refresh asynchronously
def background_refresh(key):
    """Runs periodically via cron/scheduler"""
    value = fetch_from_db(key)
    r.set(key, json.dumps(value))
```

---

## Interview Questions — Caching

### Q1: You're caching user profiles. Writes are 1% of traffic but reads are 99%. Which caching pattern do you use?

**Answer:** **Cache-Aside** with TTL + event-driven invalidation.

- Read-heavy workload → cache-aside handles the 99% reads efficiently
- On the rare writes, invalidate the cache key
- TTL as a safety net for consistency
- Write-through would work but unnecessarily updates cache on every write

---

### Q2: How would you handle cache warming for a new Redis instance?

**Answer:**
1. **Bulk load from DB:** Script that reads hot data from DB and pre-populates Redis
2. **RDB restore:** If migrating, restore an RDB backup
3. **Shadow traffic:** Route read traffic through both old and new instances
4. **Gradual rollout:** Slowly shift traffic, let cache naturally populate from misses
5. **Pipeline bulk inserts:** Use `PIPELINE` to batch thousands of `SET` commands

```python
# Cache warming script
pipe = r.pipeline()
for user in db.query("SELECT * FROM users WHERE is_active = true LIMIT 10000"):
    pipe.setex(f"user:{user.id}", 3600, json.dumps(user.to_dict()))
    if len(pipe) >= 1000:
        pipe.execute()
        pipe = r.pipeline()
pipe.execute()
```

---

### Q3: Explain the "look-aside cache" vs "inline cache" difference.

**Answer:**
- **Look-aside (Cache-Aside):** Application talks to cache AND database separately. App is responsible for keeping them in sync.
- **Inline (Read-Through / Write-Through):** Cache sits between app and DB. App only talks to cache, cache handles DB interaction.

Look-aside is simpler and far more common with Redis. Inline requires a caching layer (like a proxy or Redis modules) that understands your data model.

---

### Q4: What is the "dog-pile effect" and how do you prevent it?

**Answer:** Same as **cache stampede/thundering herd**. When a cache key expires, all concurrent requests try to rebuild it simultaneously, overloading the database.

Prevention strategies:
1. **Mutex/Lock:** Only one request rebuilds; others wait
2. **Probabilistic early refresh:** Randomly refresh before expiry
3. **Stale-while-revalidate:** Serve stale data while refreshing in background
4. **Never-expire + async refresh:** Key never expires; background job refreshes periodically
