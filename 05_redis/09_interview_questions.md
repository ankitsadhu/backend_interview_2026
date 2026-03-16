# Redis Interview Questions — Comprehensive (Beginner → Advanced)

A curated collection of interview questions across all Redis topics, organized by difficulty level.

---

## 🟢 Beginner Level

### Q1: What is Redis and why is it used?
Redis (Remote Dictionary Server) is an open-source, in-memory data structure store. It's used as:
- **Cache** — accelerate database reads
- **Database** — when persistence is enabled
- **Message broker** — via Pub/Sub and Streams
- **Session store** — fast session access

Key differentiator: Redis operates in-memory with rich data structures (not just key-value), achieving sub-millisecond latency.

---

### Q2: What are the main Redis data types?
| Type | Description | Example Use Case |
|------|-------------|-----------------|
| String | Text, numbers, binary (max 512MB) | Caching, counters |
| List | Ordered collection | Task queues, feeds |
| Set | Unordered unique elements | Tags, unique visitors |
| Sorted Set | Set with scores | Leaderboards, ranking |
| Hash | Field-value pairs | User profiles, objects |
| Stream | Append-only log | Event sourcing |
| Bitmap | Bit-level operations | Daily active users |
| HyperLogLog | Probabilistic cardinality | Unique counts |

---

### Q3: How does Redis achieve sub-millisecond latency?
1. All data in RAM (not disk)
2. Single-threaded command execution (no locks/context switching)
3. I/O multiplexing via epoll/kqueue
4. Optimized internal data structures
5. Simple RESP protocol with minimal parsing overhead

---

### Q4: What is the difference between `SET` and `SETNX`?
- `SET key value` — Always sets the key
- `SETNX key value` — Sets only if key does NOT exist
- Modern: `SET key value NX EX 30` — Atomic set-if-not-exists with 30s TTL (preferred for distributed locks)

---

### Q5: How do you delete keys with a pattern?
```bash
# NEVER use KEYS in production!
# Use SCAN instead:
redis-cli --scan --pattern "temp:*" | xargs redis-cli DEL

# Or UNLINK for async deletion:
redis-cli --scan --pattern "temp:*" | xargs redis-cli UNLINK
```

---

### Q6: What is the difference between `DEL` and `UNLINK`?
- `DEL` — Synchronous deletion. Blocks for large keys (millions of elements)
- `UNLINK` — Asynchronous deletion. Key removed from keyspace immediately, memory reclaimed by background thread

**Rule:** Always use `UNLINK` for keys that might be large.

---

## 🟡 Intermediate Level

### Q7: Explain Redis persistence options and when to use each.
| Strategy | Data Loss Risk | Performance | Use Case |
|----------|---------------|-------------|----------|
| None | 100% on crash | Best | Pure cache |
| RDB | Minutes of data | Good | Periodic backups |
| AOF (everysec) | ~1 second | Good | Data store |
| AOF (always) | None | Slower writes | Financial data |
| Hybrid | ~1 second | Good | **Production recommended** |

---

### Q8: What is the cache-aside pattern?

```
Read: Check cache → miss → query DB → populate cache → return
Write: Update DB → delete cache key (NOT update!)
```

Why delete instead of update cache on write?
- Avoids race condition where stale data overwrites fresh data
- Lazy population — only cache what's actually read

---

### Q9: Explain Redis Sentinel vs Redis Cluster.

| Feature | Sentinel | Cluster |
|---------|----------|---------|
| Purpose | High availability (failover) | Horizontal scaling + HA |
| Sharding | ❌ No | ✅ 16,384 hash slots |
| Write scaling | Single master | Multiple masters |
| Data limit | Single server RAM | Sum of all nodes |
| Complexity | Medium | High |
| Min deployment | 3 Sentinels + 1 Master + 1 Replica | 3 Masters + 3 Replicas |

---

### Q10: How does Redis handle expired keys?

Two strategies:
1. **Passive:** Checked on access — if expired, delete and return nil
2. **Active:** 10 times/sec, sample 20 random keys with TTL → delete expired → if >25% expired, repeat

This means a key can exist slightly past its TTL until accessed or sampled.

---

### Q11: What is a Redis pipeline and why use it?

Pipeline batches multiple commands into a single network round trip.

```
Without pipeline: 100 commands × 0.5ms RTT = 50ms
With pipeline:    100 commands × 1 RTT      = 0.5ms
```

Pipeline is NOT atomic — use `MULTI/EXEC` for atomicity.

---

### Q12: How would you implement a distributed lock using Redis?

```redis
-- Acquire: SET with NX and EX (atomic)
SET lock:resource <unique-id> NX EX 30

-- Release: Lua script (check ownership first)
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
end
```

Critical points:
- **NX + EX must be atomic** (single SET command)
- **Release must check ownership** (Lua script)
- **TTL prevents deadlock** if holder crashes
- For multi-instance safety, use **Redlock** (acquire on N/2+1 instances)

---

### Q13: What happens during Redis failover with Sentinel?

1. Sentinel detects master unreachable (SDOWN)
2. Majority of Sentinels confirm (ODOWN)
3. Leader Sentinel elected
4. Best replica promoted (most data, highest priority)
5. Other replicas repoint to new master
6. Clients notified via Sentinel of new master address

Data loss: Possible for writes not yet replicated (async replication).

---

## 🔴 Advanced Level

### Q14: Redis Cluster uses hash slots. What is the MOVED redirect and how do smart clients avoid it?

```
Client → Node A: GET user:1001
Node A → Client: -MOVED 12539 192.168.1.3:7002

Smart clients:
1. On startup, fetch full slot map: CLUSTER SLOTS
2. Cache slot→node mapping locally
3. Route commands directly to correct node
4. On MOVED, update local map + retry
5. On ASK, send ASKING + retry (temp redirect during migration)
```

This means most requests go to the correct node on the first try — MOVED redirects are rare after initial discovery.

---

### Q15: Explain the trade-offs of the Redlock algorithm. Is it safe?

**Martin Kleppmann's critique:**
1. Relies on **clock synchronization** — if a node's clock jumps forward, lock expires early
2. No **fencing token** — even after lock expires, old holder might still operate believing it has the lock
3. Network delays after acquiring lock can exceed TTL

**Antirez (Redis creator) response:**
1. Clock jumps are rare with NTP
2. Most systems don't need absolute safety guarantees
3. Practical: Add a fencing token (monotonic counter) for critical operations

**Verdict:**
- For **efficiency** (prevent duplicate work): Redlock is fine
- For **correctness** (financial transactions): Use a proper consensus system (ZooKeeper, etcd)

---

### Q16: How does Redis Cluster handle a network partition?

```
Partition splits cluster into two halves:

Majority side (>50% masters):
  ✅ Continues operating (quorum achieved)
  ⚠️ Promotes replicas for unreachable masters

Minority side (<50% masters):
  ❌ Stops accepting writes after cluster-node-timeout
  ❌ Returns CLUSTERDOWN errors

Resolution:
  - Minority side nodes become replicas of majority side
  - Any writes on old partitioned masters are LOST
  - Clients should implement retry + rediscovery logic
```

**Mitigation:** `min-replicas-to-write 1` ensures master stops writes if it can't reach replicas.

---

### Q17: Design a real-time recommendation engine using Redis.

**Architecture:**

```python
class RecommendationEngine:
    def __init__(self, r):
        self.r = r
    
    def track_view(self, user_id, item_id):
        """Track user → item interaction."""
        self.r.sadd(f"user:{user_id}:viewed", item_id)
        self.r.sadd(f"item:{item_id}:viewers", user_id)
        self.r.zincrby("popular", 1, item_id)
    
    def recommend_collaborative(self, user_id, n=10):
        """Find items viewed by similar users."""
        viewed = self.r.smembers(f"user:{user_id}:viewed")
        
        # Find users who viewed same items
        similar_users = set()
        for item in viewed:
            viewers = self.r.srandmember(f"item:{item}:viewers", 20)
            similar_users.update(viewers)
        similar_users.discard(user_id.encode())
        
        # Aggregate items viewed by similar users
        candidate_keys = [f"user:{uid.decode()}:viewed" for uid in similar_users]
        if candidate_keys:
            self.r.sunionstore("temp:candidates", *candidate_keys)
            self.r.sdiffstore("temp:recommendations", "temp:candidates", f"user:{user_id}:viewed")
            recs = self.r.srandmember("temp:recommendations", n)
            self.r.delete("temp:candidates", "temp:recommendations")
            return recs
        return []
    
    def recommend_popular(self, user_id, n=10):
        """Popular items not yet seen by user."""
        popular = self.r.zrevrange("popular", 0, 50)
        viewed = self.r.smembers(f"user:{user_id}:viewed")
        unseen = [item for item in popular if item not in viewed]
        return unseen[:n]
```

---

### Q18: You need to store 1 billion keys efficiently. Design the Redis architecture.

**Answer:**

**Memory estimation:**
- Key: avg 30 bytes + value: avg 100 bytes + overhead: ~70 bytes = ~200 bytes per key
- 1B × 200 bytes = **~200 GB**

**Architecture:**

```
Option 1: Redis Cluster
  - 200 GB / 32 GB per node = ~7 master nodes
  - + 7 replica nodes = 14 nodes minimum
  - Use consistent key naming with hash tags for related keys

Option 2: Client-side sharding
  - Application-level consistent hashing
  - Simpler but no automatic failover

Optimizations:
  1. Hash bucketing: Group keys into hashes (100:1 ratio)
     - 1B keys → 10M hash keys with 100 fields each
     - Saves ~60% memory (hash ziplist encoding)
  
  2. Compression: gzip values before storing
     - Reduces value size by 2-5x
     - Trades CPU for memory
  
  3. Short key names: "u:1001:p" not "user:1001:profile"
  
  4. TTL management: Ensure all keys have TTLs
```

---

### Q19: Explain Redis memory fragmentation. When does it become a problem and how do you fix it?

**Answer:**

**What:** Allocator (jemalloc) allocates memory in fixed-size chunks. Frequent alloc/free of varying sizes → memory gaps that can't be reused.

```redis
INFO memory
# mem_fragmentation_ratio: used_memory_rss / used_memory
# > 1.5: fragmentation is a problem
# < 1.0: swapping to disk (very bad!)
# 1.0-1.5: normal range
```

**Causes:**
- High key churn (frequent create/delete)
- Keys growing/shrinking (APPEND, list operations)
- Large key deletion

**Solutions:**
1. **Active defrag (Redis 4.0+):**
   ```redis
   CONFIG SET activedefrag yes
   CONFIG SET active-defrag-enabled yes
   CONFIG SET active-defrag-threshold-lower 10    -- Start when frag > 10%
   CONFIG SET active-defrag-threshold-upper 100   -- Max effort when frag > 100%
   CONFIG SET active-defrag-cycle-min 1            -- Min CPU % for defrag
   CONFIG SET active-defrag-cycle-max 25           -- Max CPU % for defrag
   ```
2. **Restart with RDB:** Load data from clean RDB (no fragmentation)
3. **Use UNLINK:** Async deletion reduces fragmentation
4. **Replica failover:** Promote freshly-synced replica (clean memory layout)

---

### Q20: Design a distributed session store for 100M concurrent users using Redis.

**Answer:**

```
Scale: 100M sessions × ~1KB per session = ~100 GB

Architecture:
┌─────────────────────────────────────────────────┐
│               Load Balancer                      │
│  (Sticky sessions NOT required)                  │
└────────────────────┬────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼───┐       ┌───▼───┐       ┌───▼───┐
│ App 1 │       │ App 2 │       │ App N │
└───┬───┘       └───┬───┘       └───┬───┘
    │                │                │
    └────────────────┼────────────────┘
                     │
        ┌────────────▼────────────┐
        │   Redis Cluster         │
        │   (10 masters × 10GB)   │
        │   + 10 replicas         │
        │                         │
        │   Slot distribution:    │
        │   session:{id} → slot   │
        └─────────────────────────┘

Session design:
  Key: session:{session_id}  (session_id = 32-char random token)
  Type: Hash
  Fields: user_id, created_at, last_access, ip, user_agent, ...
  TTL: 24 hours (refreshed on access)

Security:
  - session_id = cryptographically random (secrets.token_urlsafe(32))
  - HttpOnly, Secure, SameSite cookies
  - Bind session to IP range
  - Rate limit session creation
  - Invalidate all sessions on password change

Performance:
  - Hash type uses ~100 bytes overhead per key
  - 100M × 1.1KB = ~110 GB → 11 masters × 10GB
  - Read from replicas (READONLY mode)
  - Pipeline session refresh (GET + EXPIRE in one round trip)
```

---

## 🔥 Rapid-Fire Questions

| Question | One-Line Answer |
|----------|----------------|
| Max key size? | 512 MB (but keep keys short) |
| Max value size? | 512 MB |
| Max number of keys? | 2^32 (~4 billion) per instance |
| Is Redis thread-safe? | Yes — single-threaded command execution |
| Does Redis support transactions? | Yes — MULTI/EXEC (but no rollback) |
| Does Redis support SQL? | No — it's a key-value store with rich data structures |
| Can Redis data survive restarts? | Yes — with RDB or AOF persistence |
| What port does Redis use? | 6379 (default) |
| What is RESP? | Redis Serialization Protocol (client-server communication) |
| What language is Redis written in? | C |
| What is `redis-benchmark`? | Built-in tool to benchmark Redis performance |
| Difference between `expire` and `pexpire`? | `EXPIRE` = seconds, `PEXPIRE` = milliseconds |
| What is `redis-cli --pipe`? | Mass insertion mode (fastest way to bulk load) |
| What is `CLIENT PAUSE`? | Pauses all clients for N milliseconds (used during failover) |
| What is `OBJECT ENCODING key`? | Shows internal encoding (ziplist, hashtable, etc.) |
| What is `DUMP` / `RESTORE`? | Serialize a key → binary format → restore on another instance |
| What is `RANDOMKEY`? | Returns a random key from the database |
| What is `DBSIZE`? | Returns number of keys in current database |
| What is `CONFIG RESETSTAT`? | Reset internal statistics (INFO stats) |
| What is `SWAPDB 0 1`? | Atomically swap two databases |
