# Redis Performance, Security & Production Best Practices

## Performance Optimization

### 1. Memory Optimization

```redis
-- Check memory usage
INFO memory
MEMORY USAGE mykey                   -- Memory used by a specific key
MEMORY DOCTOR                        -- Memory analysis

-- Optimize encoding (Redis auto-selects based on thresholds)
-- Small data structures use compact encodings:
-- Hash:       ziplist (≤128 fields, ≤64 bytes each) → hashtable
-- List:       listpack (≤128 elements, ≤64 bytes each) → quicklist
-- Set:        listpack (≤128 elements, all integers) → hashtable
-- Sorted Set: listpack (≤128 elements, ≤64 bytes each) → skiplist

-- Tune thresholds to save memory
CONFIG SET hash-max-listpack-entries 128
CONFIG SET hash-max-listpack-value 64
CONFIG SET list-max-listpack-size -2
CONFIG SET set-max-intset-entries 512
CONFIG SET zset-max-listpack-entries 128
```

### Memory Optimization Techniques

| Technique | Description | Savings |
|-----------|-------------|---------|
| **Hash encoding** | Store objects as hashes instead of separate keys | 5-10x |
| **Compress values** | gzip/lz4 before storing | 2-5x |
| **Shorter key names** | `u:1001:p` vs `user:1001:profile` | 10-30% |
| **Integer sets** | Sets with only integers use compact encoding | 5x+ |
| **Shared objects** | Small integers (0-9999) are shared | Minor |
| **TTL everything** | Prevent memory leaks from forgotten keys | Prevents OOM |
| **LFU eviction** | Better hit ratio than LRU | Same memory, better cache |

```python
# Storing objects efficiently using hash buckets
# Instead of: SET user:1001:name "Alice" (one key per field)
# Use: HSET user:1001 name "Alice" age "30" (one key, multiple fields)

# Even better — hash bucketing for millions of small objects:
def set_user_field(user_id, field, value):
    bucket = user_id // 100  # Group 100 users per hash
    r.hset(f"users:{bucket}", f"{user_id}:{field}", value)

def get_user_field(user_id, field):
    bucket = user_id // 100
    return r.hget(f"users:{bucket}", f"{user_id}:{field}")
```

### 2. Command Optimization

```redis
-- ❌ SLOW: Iterate all keys
KEYS user:*                          -- O(N) — NEVER use in production!

-- ✅ FAST: Use SCAN for iteration
SCAN 0 MATCH user:* COUNT 100       -- Incremental, non-blocking

-- ❌ SLOW: Multiple GET calls
GET key1
GET key2
GET key3

-- ✅ FAST: Batch operations
MGET key1 key2 key3                  -- Single round trip

-- ❌ SLOW: Individual operations
for key in keys:
    r.set(key, value)

-- ✅ FAST: Pipeline
pipe = r.pipeline()
for key in keys:
    pipe.set(key, value)
pipe.execute()
```

### 3. Slow Log

```redis
CONFIG SET slowlog-log-slower-than 10000   -- Log commands slower than 10ms
CONFIG SET slowlog-max-len 128             -- Keep last 128 slow commands

SLOWLOG GET 10                             -- Get last 10 slow commands
SLOWLOG LEN                                -- Number of slow commands logged
SLOWLOG RESET                              -- Clear slow log
```

### 4. Dangerous Commands

| Command | Problem | Alternative |
|---------|---------|-------------|
| `KEYS *` | O(N), blocks server | `SCAN 0 MATCH * COUNT 100` |
| `FLUSHALL` | Deletes everything | Protect with `rename-command` |
| `FLUSHDB` | Deletes all in current DB | Protect with `rename-command` |
| `SAVE` | Blocks server during RDB | Use `BGSAVE` |
| `DEBUG` | Can crash server | Disable in production |
| `MONITOR` | Performance hit, outputs all commands | Use sparingly |

```redis
-- redis.conf: Rename dangerous commands
rename-command FLUSHALL ""             -- Disable completely
rename-command KEYS "KEYS_RENAMED_XYZ" -- Restrict access
rename-command DEBUG ""
```

---

## Security Best Practices

### Authentication

```redis
# redis.conf (Redis 6.0+ ACL)
requirepass "your-strong-password-here"

# ACL — fine-grained access control
ACL SETUSER reader on >password123 ~cached:* +get +mget -@dangerous
ACL SETUSER writer on >password456 ~* +@all -@dangerous
ACL SETUSER admin on >admin-pass ~* +@all

# Check ACL
ACL LIST
ACL WHOAMI
ACL GETUSER reader
```

### Network Security

```redis
# redis.conf
bind 127.0.0.1 192.168.1.100     -- Only listen on specific interfaces
protected-mode yes                 -- Reject connections without password
port 6379                          -- Default port (consider changing)

# TLS/SSL (Redis 6.0+)
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

### Security Checklist

- [ ] Set strong password (`requirepass`)
- [ ] Bind to private interfaces only
- [ ] Enable `protected-mode`
- [ ] Use ACLs for fine-grained access
- [ ] Enable TLS for encrypted connections
- [ ] Rename/disable dangerous commands
- [ ] Run as non-root user
- [ ] Use firewall rules (only allow app servers)
- [ ] Keep Redis updated (security patches)
- [ ] Don't expose Redis to the internet

---

## Production Configuration Template

```ini
# redis.conf — Production Template

# Network
bind 10.0.0.5
port 6379
protected-mode yes
tcp-backlog 511
timeout 300
tcp-keepalive 60

# Authentication
requirepass "your-strong-password"

# Memory
maxmemory 4gb
maxmemory-policy allkeys-lfu
maxmemory-samples 10

# Persistence (Hybrid)
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Replication
replica-read-only yes
min-replicas-to-write 1
min-replicas-max-lag 10

# Performance
hz 10
dynamic-hz yes
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes

# Logging
loglevel notice
logfile /var/log/redis/redis.log

# Slow Log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Security
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command DEBUG ""
rename-command KEYS "SCAN_INSTEAD"
```

---

## Monitoring & Observability

### Key Metrics to Monitor

| Metric | Command | Alert Threshold |
|--------|---------|----------------|
| Memory usage | `INFO memory` | >80% of maxmemory |
| Connected clients | `INFO clients` | >80% of maxclients |
| Hit ratio | `INFO stats` (hits/(hits+misses)) | <90% |
| Eviction rate | `INFO stats` (evicted_keys) | >0 (for non-cache) |
| Command latency | `INFO commandstats` | p99 > 10ms |
| Replication lag | `INFO replication` | >1 second |
| Memory fragmentation | `INFO memory` (mem_fragmentation_ratio) | >1.5 |
| Blocked clients | `INFO clients` (blocked_clients) | >0 (sustained) |
| Expired keys/sec | `INFO stats` | Sudden spikes |
| Connected replicas | `INFO replication` | <expected count |

```redis
-- One-liner health check
INFO server
INFO memory
INFO clients
INFO stats
INFO replication
INFO keyspace

-- Latency monitoring
CONFIG SET latency-monitor-threshold 100   -- Track commands >100ms
LATENCY LATEST
LATENCY HISTORY event-name
```

```python
# Python health check
def redis_health_check(r):
    info = r.info()
    
    checks = {
        "connected": r.ping(),
        "memory_usage_pct": info["used_memory"] / info.get("maxmemory", float("inf")) * 100,
        "hit_ratio": info["keyspace_hits"] / max(1, info["keyspace_hits"] + info["keyspace_misses"]) * 100,
        "connected_clients": info["connected_clients"],
        "evicted_keys": info["evicted_keys"],
        "replication_lag": info.get("master_repl_offset", 0) - info.get("slave_repl_offset", 0),
    }
    
    return checks
```

---

## Interview Questions — Production

### Q1: Redis is using 6 GB with `maxmemory` set to 4 GB. How is this possible?

**Answer:**
`maxmemory` only limits **data stored by users**, not Redis's internal overhead:

1. **Memory fragmentation** — allocator reserves more than needed (`mem_fragmentation_ratio`)
2. **Replication buffers** — output buffers for replicas
3. **AOF rewrite buffer** — accumulates during `BGREWRITEAOF`
4. **Client output buffers** — per-client output buffer
5. **Lua script memory** — scripts loaded in memory
6. **Copy-on-write pages** during `BGSAVE`/`BGREWRITEAOF`

**Fix:**
```redis
CONFIG SET maxmemory 3gb           -- Lower to account for overhead
CONFIG SET activedefrag yes        -- Enable active defragmentation
CONFIG SET client-output-buffer-limit normal 256mb 128mb 60
```

---

### Q2: Your Redis has a hit ratio of 60%. How do you improve it?

**Answer:**

1. **Analyze access patterns:**
   ```redis
   OBJECT FREQ key           -- LFU frequency (if maxmemory-policy = lfu)
   OBJECT IDLETIME key       -- Seconds since last access
   ```

2. **Switch to LFU eviction:** `allkeys-lfu` evicts least-frequently-used keys (better than LRU for skewed distributions)

3. **Increase memory:** More cache = fewer evictions

4. **Optimize TTLs:**
   - Increase TTL for frequently accessed keys
   - Decrease TTL for rarely accessed keys
   - Analyze: `redis-cli --bigkeys` + `redis-cli --hotkeys`

5. **Cache warming:** Pre-populate cache for predictable traffic patterns

6. **Review what's cached:** Maybe caching the wrong data

---

### Q3: How do you migrate from standalone Redis to Redis Cluster with zero downtime?

**Answer:**

**Phase 1: Preparation**
1. Audit code for multi-key commands (MGET, SUNION) — must use hash tags
2. Ensure no `SELECT` commands (Cluster only uses DB 0)

**Phase 2: Setup**
1. Deploy Redis Cluster alongside existing standalone
2. Set up dual-write: writes go to BOTH standalone and Cluster

**Phase 3: Migration**
1. Use `MIGRATE` or `redis-cli --cluster import` to copy existing data
2. Or use a replication tool like `redis-shake`

**Phase 4: Cutover**
1. Switch reads to Cluster (verify data consistency)
2. Switch writes to Cluster
3. Decommission standalone

**Phase 5: Cleanup**
1. Remove dual-write code
2. Monitor Cluster health

---

### Q4: A Redis command is taking 30 seconds. How do you debug?

**Answer:**

```redis
-- 1. Check slow log
SLOWLOG GET 10

-- 2. Check what's running right now
CLIENT LIST                        -- See connected clients and their current commands

-- 3. Check if Lua script is running
SCRIPT EXISTS <sha>

-- 4. Check big keys (scan-based, safe)
redis-cli --bigkeys

-- 5. Check memory
INFO memory
MEMORY USAGE suspicious_key

-- 6. Common culprits:
-- • KEYS * (O(N) scan of all keys)
-- • Large SORT operations
-- • Lua script without timeout
-- • SAVE (foreground RDB) instead of BGSAVE
-- • Large SUNIONSTORE / SINTERSTORE on big sets
-- • DEL on a key with millions of elements (use UNLINK instead)
```

```redis
-- Emergency: Kill long-running script
SCRIPT KILL                        -- If script hasn't written yet

-- Emergency: Kill specific client
CLIENT KILL ID <client-id>

-- Prevention:
CONFIG SET lua-time-limit 5000     -- 5s max for Lua scripts
CONFIG SET rename-command KEYS ""   -- Disable KEYS command
```
