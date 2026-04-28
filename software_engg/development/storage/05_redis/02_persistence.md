# Redis Persistence

Redis provides multiple persistence strategies to survive restarts without losing data.

---

## RDB (Redis Database) — Snapshotting

Creates **point-in-time snapshots** of the dataset at specified intervals.

### How RDB Works

```
1. Redis forks the process (copy-on-write)
2. Child process writes entire dataset to a temp .rdb file
3. When complete, atomically replaces old dump.rdb
4. Parent continues serving requests (unaffected)
```

### Configuration

```redis
# redis.conf
save 900 1        # Snapshot if ≥1 key changed in 900 seconds
save 300 10       # Snapshot if ≥10 keys changed in 300 seconds
save 60 10000     # Snapshot if ≥10,000 keys changed in 60 seconds

dbfilename dump.rdb
dir /var/lib/redis/

# Manual triggers
BGSAVE              # Background save (fork + write)
SAVE                # Foreground save (BLOCKS everything — avoid in production!)
LASTSAVE            # Timestamp of last successful save
```

### RDB Pros & Cons

| ✅ Pros | ❌ Cons |
|---------|---------|
| Compact single file — great for backups | Data loss between snapshots (up to minutes) |
| Fast restart (load binary file) | fork() can be slow with large datasets |
| Minimal performance impact (child process does work) | Memory spike during fork (copy-on-write pages) |
| Perfect for disaster recovery | Not suitable if you need minimal data loss |

---

## AOF (Append-Only File)

Logs **every write command** to a file. On restart, Redis replays the AOF to rebuild state.

### How AOF Works

```
Write Command → Append to AOF buffer → fsync to disk (per policy)

On restart: Read AOF → Replay all commands → State restored
```

### Configuration

```redis
# redis.conf
appendonly yes
appendfilename "appendonly.aof"

# fsync policies
appendfsync always     # fsync after every write (safest, slowest)
appendfsync everysec   # fsync every second (recommended — at most 1s data loss)
appendfsync no         # Let OS decide (fastest, least safe)
```

### AOF Rewrite (Compaction)

AOF grows indefinitely, so Redis periodically rewrites it:

```redis
# Automatic rewrite triggers
auto-aof-rewrite-percentage 100    # Rewrite when AOF is 100% larger than last rewrite
auto-aof-rewrite-min-size 64mb     # Don't rewrite if AOF < 64 MB

# Manual trigger
BGREWRITEAOF
```

**How rewrite works:**
1. Fork child process
2. Child scans current in-memory state
3. Writes the **minimal set of commands** to recreate current state
4. Parent buffers new writes during rewrite
5. After child finishes, parent appends buffered writes and swaps files

Example:
```
Before rewrite:
  SET counter 1
  INCR counter
  INCR counter
  INCR counter

After rewrite:
  SET counter 4     ← Just one command!
```

### AOF Pros & Cons

| ✅ Pros | ❌ Cons |
|---------|---------|
| Minimal data loss (at most 1 second with `everysec`) | Larger file than RDB |
| Human-readable log of operations | Slower restart (replays commands) |
| Automatic rewrite keeps file compact | Slightly slower writes (fsync overhead) |
| More durable than RDB | AOF rewrite uses memory (fork) |

---

## Hybrid Persistence (Redis 4.0+)

Combines the best of both worlds:

```redis
aof-use-rdb-preamble yes    # Default: yes since Redis 4.0
```

**How it works:**
1. During AOF rewrite, the child writes an **RDB snapshot** as the preamble
2. Then appends only the **AOF commands** that arrived during the rewrite
3. Result: Fast restart (RDB binary load) + minimal data loss (AOF tail)

```
┌─────────────────────────────────┐
│    RDB Preamble (binary)        │  ← Fast to load
│    [full snapshot at time T]    │
├─────────────────────────────────┤
│    AOF Suffix (text commands)   │  ← Commands after time T
│    SET key1 "val"               │
│    INCR counter                 │
└─────────────────────────────────┘
```

> **Recommendation:** Use hybrid persistence for production deployments.

---

## Persistence Decision Matrix

| Scenario | Strategy | Config |
|----------|----------|--------|
| Pure cache (data loss OK) | None | `save ""`, `appendonly no` |
| Cache with best-effort durability | RDB only | `save 60 1000` |
| Data store (minimal loss) | AOF + `everysec` | `appendonly yes`, `appendfsync everysec` |
| Maximum durability | AOF + `always` | `appendonly yes`, `appendfsync always` |
| Production recommended | Hybrid | `aof-use-rdb-preamble yes` |
| Disaster recovery | RDB backups | Periodic `BGSAVE` + offsite copy |

---

## Interview Questions — Persistence

### Q1: Your Redis instance has 30 GB of data. BGSAVE causes the OOM killer to terminate the child. How do you fix it?

**Answer:**
- `fork()` creates a copy of the page table (not data initially — copy-on-write)
- But the OS must allocate swap space for the worst case (all pages modified)
- If `vm.overcommit_memory = 0` (default), the kernel may refuse the fork

**Solutions:**
1. Set `vm.overcommit_memory = 1` (allow overcommit)
2. Add swap space as a safety net
3. Use replicas for RDB — run `BGSAVE` on the replica instead
4. Reduce dataset size or shard across multiple instances
5. Schedule `BGSAVE` during low-write periods (fewer COW pages)

---

### Q2: AOF file is 10 GB and growing. Redis restart takes 15 minutes. What do you do?

**Answer:**
1. **Enable hybrid persistence** — `aof-use-rdb-preamble yes`
   - Restart loads RDB preamble (fast binary load) + replays AOF tail (small)
2. **Trigger BGREWRITEAOF** — compacts the AOF
3. **Tune rewrite thresholds:**
   ```redis
   auto-aof-rewrite-percentage 50    # Rewrite more aggressively
   auto-aof-rewrite-min-size 64mb
   ```
4. **Consider RDB + replicas** if AOF isn't strictly needed

---

### Q3: Can you have both RDB and AOF enabled? What happens on restart?

**Answer:**
Yes, you can enable both simultaneously. On restart:
- If **AOF is enabled**, Redis loads the AOF file (it's more complete)
- If **only RDB is enabled**, Redis loads the RDB file
- AOF takes **priority** because it's typically more up-to-date

With hybrid persistence: The AOF file itself contains an RDB preamble, so it's loaded as a binary snapshot first, then remaining AOF commands are replayed.

---

### Q4: Explain the copy-on-write mechanism during BGSAVE.

**Answer:**
```
Before BGSAVE:
┌──────────────────┐
│ Parent Process    │──→ Physical Memory Pages [A][B][C][D]
└──────────────────┘

After fork():
┌──────────────────┐
│ Parent Process    │──→ Physical Memory Pages [A][B][C][D]  (shared, read-only)
└──────────────────┘                   ↑
┌──────────────────┐                   │
│ Child Process     │──────────────────┘  (same pages, read-only)
└──────────────────┘

Parent writes to page B:
┌──────────────────┐
│ Parent Process    │──→ [A][B'][C][D]   (B' = new copy of B with modifications)
└──────────────────┘
┌──────────────────┐
│ Child Process     │──→ [A][B][C][D]    (still sees original B)
└──────────────────┘
```

- OS marks all pages as **read-only** after fork
- When parent modifies a page, OS creates a **copy** of that page (COW fault)
- Child writes the original (unmodified) snapshot to disk
- Memory overhead ≈ modified pages only, not full dataset
