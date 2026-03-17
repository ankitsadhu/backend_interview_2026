# Performance & Production PostgreSQL

## Memory Configuration

### Shared Buffers

PostgreSQL's **main cache** for table and index data. All backends share this memory.

```sql
-- Recommended: 25% of total RAM
shared_buffers = '4GB'   -- For a 16GB server

-- Check hit rate (should be > 99%)
SELECT
    sum(blks_hit) AS cache_hits,
    sum(blks_read) AS disk_reads,
    round(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2) AS hit_rate
FROM pg_stat_database;
```

### Work Memory

Memory for **sorting, hashing, and hash joins** — per operation, per connection.

```sql
-- Default: 4MB (conservative)
work_mem = '32MB'

-- Caution: Total potential usage = work_mem × sort/hash ops × connections
-- 32MB × 5 ops × 100 connections = 16GB!

-- For specific expensive queries, increase per-session:
SET work_mem = '256MB';
-- Run expensive query
RESET work_mem;

-- Signs work_mem is too low:
-- EXPLAIN ANALYZE shows: "Sort Method: external merge Disk: XXXKB"
-- This means sorting spilled to disk → increase work_mem
```

### Maintenance Work Memory

Memory for **VACUUM, CREATE INDEX, ALTER TABLE ADD FOREIGN KEY**.

```sql
maintenance_work_mem = '1GB'   -- Can be set higher than work_mem (few concurrent ops)
-- Speeds up VACUUM, REINDEX, and index creation significantly
```

### Effective Cache Size

Tells the planner how much total memory is available for disk caching (shared_buffers + OS page cache).

```sql
-- Recommended: 50-75% of total RAM
effective_cache_size = '12GB'   -- For a 16GB server
-- This doesn't allocate memory — it's a hint for the query planner
-- Higher value → planner more likely to choose index scans over seq scans
```

### Memory Summary

```
16 GB Server — Recommended Config:
┌─────────────────────────────────────────────┐
│ OS & Other Processes:    2 GB               │
│ shared_buffers:          4 GB (25%)         │
│ OS Page Cache:           8 GB (automatic)   │
│ effective_cache_size:   12 GB (hint only)   │
│ work_mem:               32 MB (per op)      │
│ maintenance_work_mem:    1 GB               │
└─────────────────────────────────────────────┘
```

---

## Connection Pooling

### Why It's Critical

PostgreSQL forks a **new process per connection** (~5-10 MB each):

```
Without pooling:                    With PgBouncer:
1000 app connections                1000 app connections
  → 1000 PostgreSQL processes          → PgBouncer
  → ~10 GB memory just for            → 100 PostgreSQL processes
     connection overhead               → ~1 GB memory
```

### PgBouncer Configuration

```ini
; pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

; Pool settings
pool_mode = transaction           ; session | transaction | statement
default_pool_size = 25            ; Connections per user/database pair
max_client_conn = 1000            ; Max incoming connections
min_pool_size = 5                 ; Keep alive connections
reserve_pool_size = 5             ; Extra connections for burst
reserve_pool_timeout = 3          ; Wait time before using reserve
```

### Connection Pool Sizing

**Optimal pool size ≈ CPU cores × 2 + effective_io_concurrency**

```
8-core server with SSD:
  Pool size = 8 × 2 + 200 ≈ say 25-50 connections
  (pgbench shows diminishing returns beyond 2× cores for CPU-bound workloads)
```

> **Less is more:** More connections ≠ more throughput. Too many connections cause context switching, lock contention, and cache thrashing.

---

## Autovacuum Tuning

### Key Parameters

```sql
-- postgresql.conf
autovacuum = on
autovacuum_max_workers = 3                    -- Max concurrent workers (increase for many tables)
autovacuum_naptime = '1min'                   -- Check interval

-- When to trigger vacuum:
autovacuum_vacuum_threshold = 50              -- Base dead tuple count
autovacuum_vacuum_scale_factor = 0.2          -- + 20% of live tuples
-- Trigger = 50 + 0.2 × n_live_tup

-- When to trigger analyze:
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1

-- Speed limits (prevent I/O storms):
autovacuum_vacuum_cost_limit = 200            -- Max cost per cycle
autovacuum_vacuum_cost_delay = '2ms'          -- Pause between cycles
-- Increase cost_limit or decrease delay for faster vacuum on powerful hardware
```

### Per-Table Tuning

```sql
-- High-update table: vacuum more aggressively
ALTER TABLE hot_table SET (
    autovacuum_vacuum_scale_factor = 0.01,     -- 1% instead of 20%
    autovacuum_vacuum_threshold = 100,
    autovacuum_analyze_scale_factor = 0.005,
    autovacuum_vacuum_cost_limit = 1000        -- Faster vacuum
);

-- Large, mostly-static table: vacuum less frequently
ALTER TABLE static_table SET (
    autovacuum_vacuum_scale_factor = 0.5,      -- 50%
    autovacuum_vacuum_threshold = 10000
);
```

### Monitoring Autovacuum

```sql
-- Tables needing vacuum most urgently
SELECT
    schemaname, relname,
    n_live_tup, n_dead_tup,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
    last_vacuum, last_autovacuum,
    last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Currently running autovacuum workers
SELECT pid, datname, relid::regclass, phase,
       heap_blks_total, heap_blks_scanned, heap_blks_vacuumed
FROM pg_stat_progress_vacuum;

-- Check for tables approaching TX ID wraparound
SELECT c.oid::regclass AS table_name,
       age(c.relfrozenxid) AS xid_age,
       pg_size_pretty(pg_total_relation_size(c.oid)) AS size
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE c.relkind = 'r' AND n.nspname NOT IN ('pg_catalog', 'information_schema')
ORDER BY age(c.relfrozenxid) DESC
LIMIT 20;
```

---

## Query Performance Monitoring

### pg_stat_statements

The **most important extension** for identifying slow queries.

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all

-- Top queries by total time
SELECT
    calls,
    round(total_exec_time::numeric, 2) AS total_ms,
    round(mean_exec_time::numeric, 2) AS avg_ms,
    round(stddev_exec_time::numeric, 2) AS stddev_ms,
    rows,
    query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Top queries by calls (most frequent)
SELECT calls, query
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

### Slow Query Logging

```sql
-- postgresql.conf
log_min_duration_statement = 200     -- Log queries > 200ms
log_statement = 'none'               -- Don't log all statements (performance)
log_checkpoints = on
log_lock_waits = on                  -- Log lock waits > deadlock_timeout
log_temp_files = 0                   -- Log any temp file usage (sorts/hashes on disk)
```

### Key Statistics Views

```sql
-- Table I/O statistics
SELECT relname,
    heap_blks_read, heap_blks_hit,
    idx_blks_read, idx_blks_hit
FROM pg_statio_user_tables
ORDER BY heap_blks_read DESC;

-- Index usage
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Database-level statistics
SELECT datname, numbackends, xact_commit, xact_rollback,
    blks_read, blks_hit, tup_returned, tup_fetched,
    tup_inserted, tup_updated, tup_deleted,
    conflicts, deadlocks
FROM pg_stat_database
WHERE datname = current_database();
```

---

## Security Best Practices

### Authentication (pg_hba.conf)

```
# TYPE    DATABASE    USER        ADDRESS        METHOD
local     all         postgres                   peer           -- OS user auth
host      all         app_user    10.0.0.0/8     scram-sha-256  -- Password
host      replication replicator  10.0.1.0/24    scram-sha-256
hostssl   all         all         0.0.0.0/0      scram-sha-256  -- SSL required
```

### Role-Based Access Control

```sql
-- Create roles (groups)
CREATE ROLE readonly;
CREATE ROLE readwrite;

-- Grant permissions
GRANT CONNECT ON DATABASE mydb TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;

GRANT readonly TO readwrite;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite;

-- Create users and assign roles
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT readwrite TO app_user;

CREATE USER reporting_user WITH PASSWORD 'secure_password';
GRANT readonly TO reporting_user;
```

### Row-Level Security (RLS)

```sql
-- Multi-tenant security at the database level
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.current_tenant')::bigint);

-- In application code:
SET app.current_tenant = '42';
SELECT * FROM orders;  -- Only sees tenant 42's orders
```

### SSL/TLS

```sql
-- postgresql.conf
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
ssl_ca_file = '/path/to/ca.crt'          -- For client cert verification
ssl_min_protocol_version = 'TLSv1.3'     -- Enforce TLS 1.3

-- Verify SSL status
SELECT ssl, version FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

---

## Backup Strategies

### pg_dump (Logical Backup)

```bash
# Full database backup
pg_dump -U postgres -h localhost mydb > backup.sql

# Custom format (compressed, parallel restore)
pg_dump -U postgres -h localhost -Fc mydb > backup.dump

# Specific tables
pg_dump -U postgres -t users -t orders mydb > tables.sql

# Parallel dump (custom format, multiple jobs)
pg_dump -U postgres -Fd -j 4 mydb -f backup_dir/

# All databases
pg_dumpall -U postgres > all_databases.sql
```

### pg_restore

```bash
# Restore from custom format
pg_restore -U postgres -d mydb -j 4 backup.dump

# Restore specific table
pg_restore -U postgres -d mydb -t users backup.dump

# List contents of backup
pg_restore -l backup.dump
```

### pg_basebackup (Physical Backup)

```bash
# Full cluster backup (for PITR and replication)
pg_basebackup -h primary -U replicator -D /backups/base \
    --checkpoint=fast --wal-method=stream -P --compress=gzip
```

### Backup Strategy Matrix

| Method | Speed | Size | PITR | Granularity | Lock? |
|--------|-------|------|------|-------------|-------|
| pg_dump | Slow | Small | No | Per table | No (MVCC snapshot) |
| pg_basebackup | Fast | Large | Yes (with WAL archiving) | Full cluster | No |
| pgBackRest | Fast | Incremental | Yes | Full cluster | No |
| Barman | Fast | Incremental | Yes | Full cluster | No |

---

## Essential Production Configuration

```sql
-- postgresql.conf — Production Template (16GB RAM, SSD, 8 cores)

-- Memory
shared_buffers = '4GB'
effective_cache_size = '12GB'
work_mem = '32MB'
maintenance_work_mem = '1GB'
huge_pages = try

-- WAL
wal_level = replica
max_wal_size = '4GB'
min_wal_size = '1GB'
wal_compression = on
wal_buffers = '64MB'            -- Auto-tunes otherwise

-- Checkpoints
checkpoint_timeout = '10min'
checkpoint_completion_target = 0.9

-- Query Planner
random_page_cost = 1.1          -- SSD (default 4.0 for HDD)
effective_io_concurrency = 200  -- SSD (default 1 for HDD)
default_statistics_target = 200

-- Parallelism
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

-- Connections
max_connections = 200           -- Use PgBouncer in front!
superuser_reserved_connections = 3

-- Autovacuum
autovacuum_max_workers = 4
autovacuum_vacuum_cost_limit = 800
autovacuum_vacuum_cost_delay = '2ms'

-- Logging
log_min_duration_statement = 200
log_checkpoints = on
log_lock_waits = on
log_temp_files = 0

-- Extensions
shared_preload_libraries = 'pg_stat_statements'
```

---

## Common Interview Questions

### Q1: How do you handle connection exhaustion?

**Symptoms:** `FATAL: too many connections for role "app_user"`

**Immediate fix:**
```sql
-- Check active connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

-- Terminate idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < now() - interval '10 minutes';
```

**Long-term solutions:**
1. Use **PgBouncer** in transaction mode (pool_mode = transaction)
2. Set `idle_in_transaction_session_timeout` to kill idle-in-transaction
3. Set `statement_timeout` to prevent runaway queries
4. Review application connection management (connection leaks?)
5. Increase `max_connections` only as last resort (memory cost)

---

### Q2: A table with 100M rows is slow. What do you do?

Systematic approach:

1. **Check table and index bloat** — Run `VACUUM FULL` if > 50% dead tuples
2. **Check index effectiveness** — Are the right indexes in place? Unused indexes?
3. **Check statistics** — `ANALYZE` the table, increase `default_statistics_target`
4. **Check query plans** — `EXPLAIN (ANALYZE, BUFFERS)` for slow queries
5. **Consider partitioning** — If queries filter by date/category, partition the table
6. **Tune configuration** — `work_mem`, `effective_cache_size`, `random_page_cost`
7. **Consider read replicas** — Offload read queries
8. **Consider materialized views** — Pre-compute expensive aggregations

---

### Q3: How do you monitor PostgreSQL in production?

**Key metrics to monitor:**

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Replication lag | `pg_stat_replication` | > 1 minute |
| Connection count | `pg_stat_activity` | > 80% of max |
| Cache hit rate | `pg_stat_database` | < 99% |
| Dead tuples | `pg_stat_user_tables` | > 10% of live tuples |
| TX ID age | `age(relfrozenxid)` | > 500 million |
| Lock waits | `pg_stat_activity` | Any long waits |
| Slow queries | `pg_stat_statements` | Mean time increase |
| Disk usage | OS metrics | > 80% |

**Tools:** pg_stat_statements, pgBadger (log analysis), Prometheus + Grafana (metrics), PgHero (dashboard)

---

### Q4: Explain the difference between `VACUUM` and `VACUUM FULL`.

| Feature | VACUUM | VACUUM FULL |
|---------|--------|-------------|
| **Lock** | No lock (concurrent) | **ACCESS EXCLUSIVE** (blocks all) |
| **Space reclaim** | Marks space for reuse | **Returns space to OS** |
| **Speed** | Fast | Slow (rewrites entire table) |
| **Table size after** | Same (or slightly smaller) | Significantly smaller |
| **When to use** | Regular maintenance (autovacuum) | Severe bloat (>50% dead) |
| **Downtime** | None | **Table is inaccessible** |
| **Alternative** | - | `pg_repack` (no lock!) |

```sql
-- Better alternative to VACUUM FULL:
CREATE EXTENSION pg_repack;
-- Repacks table without exclusive lock
-- pg_repack --table=bloated_table -d mydb
```
