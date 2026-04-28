# Replication & High Availability in PostgreSQL

## Write-Ahead Log (WAL)

Everything in PostgreSQL starts with **WAL** — the foundation of durability, replication, and recovery.

### How WAL Works

```
Transaction: UPDATE accounts SET balance = 500 WHERE id = 1;

Step 1: Write change to WAL buffer (in memory)
Step 2: At COMMIT → flush WAL buffer to WAL files on disk  ← Durability guaranteed!
Step 3: Eventually → write actual data page to data file (lazy)

Crash Recovery:
  On startup → replay WAL from last checkpoint → data is consistent
```

### WAL Structure

```
pg_wal/
├── 000000010000000000000001    ← WAL segment (16 MB default)
├── 000000010000000000000002
├── 000000010000000000000003
└── ...
```

```sql
-- View current WAL position
SELECT pg_current_wal_lsn();        -- Log Sequence Number
SELECT pg_current_wal_insert_lsn(); -- Latest insert LSN

-- WAL configuration
wal_level = replica            -- minimal | replica | logical
max_wal_size = '2GB'           -- Trigger checkpoint
min_wal_size = '80MB'          -- Keep at least this much WAL
wal_compression = on           -- Compress WAL (PG 15+)
```

### Checkpoints

Checkpoints write **all dirty pages** from shared buffers to disk, creating a known-good recovery point.

```sql
-- Key checkpoint settings
checkpoint_timeout = '5min'         -- Max time between checkpoints
checkpoint_completion_target = 0.9  -- Spread I/O over 90% of checkpoint interval
max_wal_size = '2GB'                -- Trigger checkpoint if WAL exceeds this

-- Manual checkpoint (rarely needed in production)
CHECKPOINT;
```

---

## Streaming Replication (Physical)

Replicates the **entire database cluster** at the byte level by streaming WAL records.

### Architecture

```
                     WAL Stream
  ┌──────────┐  ──────────────────►  ┌──────────┐
  │  Primary  │                      │  Replica  │
  │  (R/W)    │  ──────────────────► │  (R/O)    │
  └──────────┘   WAL records         └──────────┘
       │                                   │
       ▼                                   ▼
  Data Files                          Data Files
  WAL Files                          (identical copy)
```

### Setup — Primary Server

```sql
-- postgresql.conf (Primary)
wal_level = replica                -- Required for replication
max_wal_senders = 5                -- Max concurrent replicas
wal_keep_size = '1GB'              -- Keep WAL for slower replicas

-- pg_hba.conf (allow replica connections)
-- TYPE  DATABASE    USER           ADDRESS          METHOD
host    replication  replicator     10.0.0.0/8       scram-sha-256

-- Create replication user
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'secret';
```

### Setup — Replica Server

```bash
# Take base backup from primary
pg_basebackup -h primary-host -U replicator -D /var/lib/postgresql/data \
    --checkpoint=fast --wal-method=stream -P

# This creates a full copy of the primary's data directory
```

```sql
-- postgresql.conf (Replica)
hot_standby = on                   -- Allow read queries on replica

-- Create standby.signal file (PostgreSQL 12+)
-- Just create an empty file:
-- touch /var/lib/postgresql/data/standby.signal

-- postgresql.conf (Replica) — connection to primary
primary_conninfo = 'host=primary-host port=5432 user=replicator password=secret'
```

### Monitoring Replication

```sql
-- On Primary: check connected replicas
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replay_lag_bytes,
    reply_time
FROM pg_stat_replication;

-- On Replica: check replication status
SELECT
    pg_is_in_recovery() AS is_replica,
    pg_last_wal_receive_lsn() AS received_lsn,
    pg_last_wal_replay_lsn() AS replayed_lsn,
    pg_last_xact_replay_timestamp() AS last_replayed_at,
    now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

### Synchronous Replication

By default, replication is **asynchronous** (primary doesn't wait for replica to confirm).

```sql
-- postgresql.conf (Primary)
synchronous_commit = on                    -- Wait for sync replica
synchronous_standby_names = 'replica1'     -- Name of sync replica

-- Trade-offs:
-- Async: Faster writes, possible data loss on primary failure
-- Sync:  Slower writes (network round-trip), zero data loss
```

| Mode | Durability | Performance |
|------|-----------|-------------|
| `off` | No guarantee (crash can lose recent commits) | Fastest |
| `local` | Durable on primary | Fast |
| `remote_write` | Written to replica OS cache | Medium |
| `on` (default) | Flushed to replica WAL | Slower |
| `remote_apply` | Applied on replica (visible to queries) | Slowest |

---

## Logical Replication (PostgreSQL 10+)

Replicates specific **tables** (not entire cluster) by decoding WAL into logical changes.

### Streaming vs Logical Replication

| Feature | Streaming (Physical) | Logical |
|---------|---------------------|---------|
| Granularity | Entire cluster | Per-table |
| Replica writable | No (read-only) | **Yes** |
| Cross-version | Must match major version | Can differ |
| Cross-platform | Must match OS | Can differ |
| DDL replication | Yes (automatic) | No (manual) |
| Selective | No | Yes (filter tables/rows) |
| Use case | HA failover, read replicas | Data integration, migration, CDC |

### Setup

```sql
-- postgresql.conf (Publisher)
wal_level = logical

-- Publisher: Create publication
CREATE PUBLICATION my_pub FOR TABLE users, orders;
-- or all tables:
CREATE PUBLICATION my_pub FOR ALL TABLES;
-- or with row filter (PG 15+):
CREATE PUBLICATION my_pub FOR TABLE orders WHERE (status = 'completed');

-- Subscriber: Create subscription
CREATE SUBSCRIPTION my_sub
    CONNECTION 'host=publisher-host port=5432 dbname=mydb user=replicator password=secret'
    PUBLICATION my_pub;

-- Tables must exist on subscriber with matching schema!
```

### Change Data Capture (CDC)

Logical replication enables CDC — streaming row-level changes to external systems.

```sql
-- Create logical replication slot
SELECT pg_create_logical_replication_slot('my_slot', 'pgoutput');

-- Read changes (for CDC tools like Debezium)
SELECT * FROM pg_logical_slot_peek_changes('my_slot', NULL, NULL);
-- Shows: lsn, xid, data (INSERT/UPDATE/DELETE statements)
```

---

## Point-in-Time Recovery (PITR)

Recover to **any point in time** by replaying WAL records up to a specific timestamp.

### Setup — Continuous Archiving

```sql
-- postgresql.conf
archive_mode = on
archive_command = 'cp %p /archive/%f'  -- Copy WAL segments to archive
-- Use pgBackRest or Barman in production instead of cp
```

### Recovery Process

```bash
# 1. Restore base backup
pg_basebackup -h primary -U replicator -D /recovery/data -P

# 2. Configure recovery target
# postgresql.conf (in recovery data directory):
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2026-03-16 14:30:00 UTC'
recovery_target_action = 'promote'  -- Become primary after recovery

# 3. Create recovery signal file
touch /recovery/data/recovery.signal

# 4. Start PostgreSQL — it will replay WAL up to the target time
pg_ctl -D /recovery/data start
```

---

## Failover Strategies

### Manual Promotion

```bash
# Promote replica to primary
pg_ctl promote -D /var/lib/postgresql/data

# or via SQL (PostgreSQL 12+)
SELECT pg_promote();
```

### Patroni (Automated Failover)

Industry-standard HA solution using **DCS** (etcd/Consul/ZooKeeper) for consensus.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Patroni     │     │   Patroni     │     │   Patroni     │
│ + PostgreSQL  │     │ + PostgreSQL  │     │ + PostgreSQL  │
│   (Primary)   │     │   (Replica)   │     │   (Replica)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────┬───────┘────────────────────┘
                    │
              ┌─────▼─────┐
              │   etcd     │  ← Distributed consensus
              │  cluster   │    (leader election)
              └────────────┘
                    │
              ┌─────▼─────┐
              │  HAProxy   │  ← Routes traffic to current primary
              │  /PgBouncer│
              └────────────┘
```

**Patroni handles:**
- Automatic leader election
- Automatic failover (promotes healthiest replica)
- Automatic replication setup for new nodes
- Rolling restarts for config changes
- Switchover (planned primary change)

---

### PgBouncer (Connection Pooling)

Not HA by itself, but **essential** for production PostgreSQL.

```
Application (1000 connections)
        │
        ▼
  ┌──────────┐
  │ PgBouncer │  ← Pool manager
  │  (100 conn│     Multiplexes 1000 app connections
  │   pool)   │     into 100 PostgreSQL connections
  └─────┬─────┘
        │
        ▼
  PostgreSQL (100 actual connections)
```

**Pooling modes:**

| Mode | Description | Best for |
|------|-------------|----------|
| **Session** | Connection assigned for entire client session | Simple, long-lived connections |
| **Transaction** | Connection assigned per transaction | Most recommended for web apps |
| **Statement** | Connection assigned per statement | Autocommit only workloads |

---

## Common Interview Questions

### Q1: Explain the difference between streaming and logical replication.

**Streaming (Physical):**
- Replicates **WAL bytes** (entire cluster)
- Replica is byte-for-byte identical
- Read-only replica
- Same PostgreSQL version required
- Use for: HA failover, read scaling

**Logical:**
- Replicates **logical changes** (INSERT/UPDATE/DELETE per table)
- Selective (specific tables, row filters)
- Subscriber can write to its own tables
- Cross-version, cross-platform
- Use for: Data integration, online migration, CDC

---

### Q2: How do you handle failover in PostgreSQL?

1. **Detection** — Monitor replication lag, run health checks (Patroni does this automatically)
2. **Promotion** — `pg_promote()` on the most up-to-date replica
3. **Routing** — Update DNS/load balancer to point to new primary (HAProxy, PgBouncer)
4. **Re-sync** — Old primary must be rebuilt as a replica using `pg_rewind` or `pg_basebackup`
5. **Verification** — Check data consistency, replication lag on remaining replicas

**Automatic failover:** Use Patroni + etcd + HAProxy for production-grade HA.

---

### Q3: What is replication lag and how do you minimize it?

**Replication lag** = delay between a write on primary and its availability on replica.

**Causes:**
1. Network latency between primary and replica
2. Replica is under heavy read load (CPU-bound)
3. Large transactions (long WAL replay)
4. Disk I/O bottleneck on replica

**Minimize lag:**
1. **Ensure replica has equal or better hardware** than primary
2. **Use synchronous replication** for zero lag (at cost of write performance)
3. **Distribute read load** across multiple replicas
4. **Monitor** `pg_stat_replication` and alert on lag thresholds
5. **Tune** `max_parallel_workers_per_gather` on replica for faster replay

---

### Q4: How do you perform a zero-downtime PostgreSQL major version upgrade?

**Option 1: Logical Replication Migration**

```
1. Set up new PG cluster (new version)
2. Create matching schema on new cluster
3. Set up logical replication (old → new)
4. Wait for initial sync to complete
5. Monitor replication lag → wait until near-zero
6. Stop writes to old cluster (brief downtime)
7. Wait for final sync
8. Switch application connection string to new cluster
9. Tear down old cluster
```

**Option 2: pg_upgrade (in-place, requires downtime)**

```bash
pg_upgrade --old-bindir=/usr/lib/postgresql/15/bin \
           --new-bindir=/usr/lib/postgresql/16/bin \
           --old-datadir=/var/lib/postgresql/15/main \
           --new-datadir=/var/lib/postgresql/16/main \
           --link  # Hard-link files (fast, but shares disk)

# With --link: minutes of downtime
# Without --link: hours (copies all data)
```
