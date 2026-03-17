# Transactions & Concurrency in PostgreSQL

## ACID Properties

| Property | Description | PostgreSQL Implementation |
|----------|-------------|--------------------------|
| **Atomicity** | All or nothing — transactions fully succeed or fully rollback | WAL (Write-Ahead Log) ensures undo |
| **Consistency** | Data satisfies all constraints after transaction | Constraints checked at commit (or statement) |
| **Isolation** | Concurrent transactions don't interfere | MVCC (Multi-Version Concurrency Control) |
| **Durability** | Committed data survives crashes | WAL flushed to disk on commit |

---

## Transaction Basics

```sql
-- Implicit transaction (autocommit)
INSERT INTO users (name) VALUES ('Alice');  -- Committed immediately

-- Explicit transaction
BEGIN;
    INSERT INTO users (name) VALUES ('Bob');
    UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE user_id = 2;
COMMIT;

-- Rollback
BEGIN;
    DELETE FROM users WHERE id = 999;
    -- Oops!
ROLLBACK;  -- Nothing was deleted

-- Savepoints (partial rollback)
BEGIN;
    INSERT INTO orders (item) VALUES ('Widget');
    SAVEPOINT sp1;
    INSERT INTO orders (item) VALUES ('Gadget');
    -- Error occurred
    ROLLBACK TO sp1;  -- Only 'Gadget' insert is rolled back
    INSERT INTO orders (item) VALUES ('Gizmo');
COMMIT;  -- Widget and Gizmo are committed
```

---

## MVCC (Multi-Version Concurrency Control)

PostgreSQL's concurrency model: **readers never block writers, writers never block readers**.

### How MVCC Works

Every row has hidden system columns:

| Column | Description |
|--------|-------------|
| `xmin` | Transaction ID that **inserted** this row version |
| `xmax` | Transaction ID that **deleted/updated** this row version (0 if active) |
| `ctid` | Physical location (page, offset) of this row version |

```sql
-- View hidden columns
SELECT xmin, xmax, ctid, * FROM users LIMIT 5;
```

### MVCC Example

```
Time  Transaction T1 (xid=100)           Transaction T2 (xid=101)
────  ─────────────────────────           ─────────────────────────
  1   BEGIN;                              BEGIN;
  2   UPDATE users                        
      SET name='Bob'                      
      WHERE id=1;                         
      -- Creates NEW row version          
      -- Old: xmin=50, xmax=100          
      -- New: xmin=100, xmax=0           
  3                                       SELECT * FROM users WHERE id=1;
                                          -- Sees OLD version (xmin=50)
                                          -- Because T1 not yet committed
  4   COMMIT;                             
  5                                       SELECT * FROM users WHERE id=1;
                                          -- What T2 sees depends on
                                          -- ISOLATION LEVEL!
```

### Tuple Visibility Rules

A tuple is **visible** to transaction T if:
1. `xmin` is committed AND `xmin` was committed before T started (or is T itself)
2. AND (`xmax` is 0 OR `xmax` is not committed OR `xmax` committed after T's snapshot)

---

## Isolation Levels

```sql
-- Set for current transaction
BEGIN ISOLATION LEVEL READ COMMITTED;

-- Set session default
SET default_transaction_isolation = 'repeatable read';
```

### Read Committed (Default)

Each **statement** sees the latest committed data at the time the statement starts.

```
T1: BEGIN;
T1: SELECT balance FROM accounts WHERE id = 1;  -- Sees 1000

T2: UPDATE accounts SET balance = 500 WHERE id = 1;
T2: COMMIT;

T1: SELECT balance FROM accounts WHERE id = 1;  -- Sees 500 ← NEW snapshot per statement!
T1: COMMIT;
```

**Phenomena allowed:** Non-repeatable reads, phantom reads
**Phenomena prevented:** Dirty reads

---

### Repeatable Read

Transaction sees a **snapshot** as of the transaction start. Same query returns same results.

```
T1: BEGIN ISOLATION LEVEL REPEATABLE READ;
T1: SELECT balance FROM accounts WHERE id = 1;  -- Sees 1000

T2: UPDATE accounts SET balance = 500 WHERE id = 1;
T2: COMMIT;

T1: SELECT balance FROM accounts WHERE id = 1;  -- Still sees 1000!

T1: UPDATE accounts SET balance = balance + 100 WHERE id = 1;
-- ERROR: could not serialize access due to concurrent update
-- T1 must retry!
```

**Phenomena prevented:** Dirty reads, non-repeatable reads, phantom reads
**Trade-off:** Serialization errors require application-level retry logic

---

### Serializable

Strongest level. Transactions behave **as if executed one at a time**.

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

Uses **SSI (Serializable Snapshot Isolation)** — detects dependency cycles and aborts one transaction.

```
T1: SELECT SUM(amount) FROM transactions WHERE account = 'A';  -- reads A
T2: SELECT SUM(amount) FROM transactions WHERE account = 'B';  -- reads B
T1: INSERT INTO transactions (account, amount) VALUES ('B', ...);  -- writes B
T2: INSERT INTO transactions (account, amount) VALUES ('A', ...);  -- writes A
-- One of these MUST be aborted (rw-dependency cycle detected)
```

**When to use:** Financial systems, inventory management, anywhere correctness > performance.
**Cost:** Higher abort rate, applications MUST retry failed transactions.

---

### Isolation Level Summary

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Serialization Anomaly |
|-------|-----------|--------------------|--------------|-----------------------|
| Read Committed | ❌ | ✅ | ✅ | ✅ |
| Repeatable Read | ❌ | ❌ | ❌* | ✅ |
| Serializable | ❌ | ❌ | ❌ | ❌ |

> *PostgreSQL's Repeatable Read also prevents phantom reads (stricter than SQL standard).

> **Note:** PostgreSQL does NOT support Read Uncommitted — it's treated as Read Committed.

---

## Locking

### Row-Level Locks

```sql
-- SELECT ... FOR UPDATE (exclusive lock on selected rows)
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- Other transactions BLOCK on UPDATE/DELETE of this row
-- Other transactions can still SELECT (MVCC!)
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- FOR SHARE (shared lock — blocks writes but allows other FOR SHARE)
SELECT * FROM products WHERE id = 5 FOR SHARE;

-- SKIP LOCKED (skip rows locked by other transactions — great for job queues!)
SELECT * FROM jobs
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;

-- NOWAIT (fail immediately if row is locked)
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- ERROR: could not obtain lock on row (instead of waiting)
```

### Lock Modes

| Lock Mode | Conflicts With | Use Case |
|-----------|---------------|----------|
| `FOR UPDATE` | UPDATE, DELETE, FOR UPDATE, FOR SHARE | Exclusive row modification |
| `FOR NO KEY UPDATE` | UPDATE, DELETE, FOR UPDATE | Update non-key columns |
| `FOR SHARE` | UPDATE, DELETE, FOR UPDATE | Read-only lock |
| `FOR KEY SHARE` | FOR UPDATE | FK reference checking |

### Table-Level Locks

```sql
-- Explicit table lock (rarely needed)
LOCK TABLE users IN ACCESS EXCLUSIVE MODE;

-- DDL operations acquire locks automatically:
-- ALTER TABLE → AccessExclusiveLock (blocks everything!)
-- CREATE INDEX → ShareLock (blocks writes)
-- CREATE INDEX CONCURRENTLY → ShareUpdateExclusiveLock (allows reads AND writes)
```

### Lock Modes Matrix (Table-Level)

| Lock Mode | Blocks |
|-----------|--------|
| ACCESS SHARE | Only ACCESS EXCLUSIVE |
| ROW SHARE | EXCLUSIVE, ACCESS EXCLUSIVE |
| ROW EXCLUSIVE | SHARE, SHARE ROW EXCLUSIVE, EXCLUSIVE, ACCESS EXCLUSIVE |
| SHARE UPDATE EXCLUSIVE | SHARE UPDATE EXCLUSIVE, SHARE, ↑ |
| SHARE | ROW EXCLUSIVE, SHARE UPDATE EXCLUSIVE, ↑ |
| SHARE ROW EXCLUSIVE | ROW EXCLUSIVE, ↑ |
| EXCLUSIVE | ROW SHARE, ↑ |
| ACCESS EXCLUSIVE | Everything |

---

## Advisory Locks

Application-level locks that don't lock any actual database object.

```sql
-- Session-level advisory lock
SELECT pg_advisory_lock(12345);           -- Blocks until acquired
-- ... do work ...
SELECT pg_advisory_unlock(12345);

-- Try lock (non-blocking)
SELECT pg_try_advisory_lock(12345);       -- Returns true/false

-- Transaction-level advisory lock (auto-released at COMMIT/ROLLBACK)
SELECT pg_advisory_xact_lock(12345);

-- Two-argument form (namespace + id)
SELECT pg_advisory_lock(1, 42);           -- Lock category 1, item 42
```

**Use Cases:**
- Application-level mutual exclusion (cron job deduplication)
- Rate limiting
- Leader election
- Resource coordination across application instances

```sql
-- Example: Prevent duplicate cron job execution
-- In your application:
IF pg_try_advisory_lock(hashtext('daily_report_job')) THEN
    -- Run the job
    -- Lock auto-releases when connection closes
END IF;
```

---

## Deadlocks

Deadlocks occur when two transactions wait for each other's locks.

```
T1: BEGIN; UPDATE accounts SET balance = 0 WHERE id = 1;  -- Locks row 1
T2: BEGIN; UPDATE accounts SET balance = 0 WHERE id = 2;  -- Locks row 2
T1: UPDATE accounts SET balance = 0 WHERE id = 2;         -- Waits for T2...
T2: UPDATE accounts SET balance = 0 WHERE id = 1;         -- Waits for T1... DEADLOCK!
```

**PostgreSQL detects deadlocks** automatically (default check every 1s via `deadlock_timeout`) and aborts one transaction:

```
ERROR: deadlock detected
DETAIL: Process 1234 waits for ShareLock on transaction 5678;
        blocked by process 5678.
        Process 5678 waits for ShareLock on transaction 1234;
        blocked by process 1234.
```

### Preventing Deadlocks

1. **Lock rows in consistent order** (always lock by ascending ID)
2. **Keep transactions short** (reduce lock hold time)
3. **Use `NOWAIT`** or `lock_timeout` to fail fast
4. **Avoid user interaction** inside transactions

```sql
-- Set lock timeout
SET lock_timeout = '5s';  -- Fail if can't acquire lock within 5 seconds
```

---

## VACUUM

MVCC leaves **dead tuples** (old row versions) behind. `VACUUM` reclaims this space.

### Why VACUUM is Needed

```
UPDATE users SET name = 'Bob' WHERE id = 1;
-- Old tuple: (id=1, name='Alice') ← DEAD (xmax set)
-- New tuple: (id=1, name='Bob')   ← LIVE

-- Dead tuples waste space and slow down scans
-- VACUUM marks dead tuple space as reusable
```

### VACUUM Types

```sql
-- Standard VACUUM (marks space as reusable, doesn't return space to OS)
VACUUM users;

-- VACUUM FULL (rewrites table, returns space to OS — LOCKS TABLE!)
VACUUM FULL users;

-- VACUUM ANALYZE (vacuum + update statistics)
VACUUM ANALYZE users;

-- VACUUM VERBOSE (show details)
VACUUM VERBOSE users;
```

| | VACUUM | VACUUM FULL |
|---|--------|-------------|
| Locks table | No (can run concurrently) | **Yes** (ACCESS EXCLUSIVE) |
| Reclaims space | Marks for reuse | Returns to OS |
| Speed | Fast | Slow (rewrites entire table) |
| Use when | Regular maintenance | Table has significant bloat |

### Autovacuum

PostgreSQL automatically vacuums tables via the **autovacuum** daemon.

```sql
-- Key autovacuum settings (postgresql.conf)
autovacuum = on                             -- Enable (default)
autovacuum_vacuum_threshold = 50            -- Min dead tuples before vacuum
autovacuum_vacuum_scale_factor = 0.2        -- + 20% of table rows
-- Trigger = threshold + scale_factor × n_live_tup
-- For 10,000 row table: 50 + 0.2 × 10000 = 2050 dead tuples

autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1

-- For high-update tables, lower the thresholds:
ALTER TABLE hot_table SET (
    autovacuum_vacuum_scale_factor = 0.01,    -- 1% instead of 20%
    autovacuum_vacuum_threshold = 100
);
```

### Transaction ID Wraparound

PostgreSQL uses 32-bit transaction IDs (2^31 ≈ 2.1 billion transactions).

**Problem:** If a table isn't vacuumed for ~2 billion transactions, the database will **shut down** to prevent data loss (transaction ID wraparound).

```sql
-- Check how close you are to wraparound
SELECT
    datname,
    age(datfrozenxid) AS xid_age,
    round(100.0 * age(datfrozenxid) / 2147483647, 2) AS pct_to_wraparound
FROM pg_database
ORDER BY xid_age DESC;
```

**Prevention:** Autovacuum's **anti-wraparound vacuum** kicks in at `autovacuum_freeze_max_age` (default: 200 million).

---

## Common Interview Questions

### Q1: Explain MVCC and why PostgreSQL uses it.

MVCC keeps **multiple versions** of each row. Each transaction sees a consistent **snapshot** of the database:

- **Writers create new row versions** (don't overwrite)
- **Readers see the version valid at their snapshot**
- **No read-write blocking** — reads never block writes, writes never block reads
- **Dead versions cleaned up by VACUUM**

**Trade-off:** Higher storage usage, need for VACUUM, but excellent concurrent read performance.

---

### Q2: What happens if autovacuum stops working?

1. **Table bloat** — Dead tuples accumulate, table grows, queries slow down
2. **Index bloat** — Indexes grow with dead entries
3. **Stale statistics** — Query planner makes bad decisions
4. **Transaction ID wraparound** — After ~2 billion transactions, PostgreSQL **refuses all writes** and shuts down
5. **Performance degradation** — Each seq scan processes more dead tuples

**Fix:** Monitor `n_dead_tup` in `pg_stat_user_tables`, alert if autovacuum hasn't run recently.

---

### Q3: How do you handle concurrent updates to the same row?

**Approach 1: Optimistic Locking (application-level)**

```sql
-- Add version column
ALTER TABLE products ADD COLUMN version integer DEFAULT 1;

-- Read
SELECT id, name, price, version FROM products WHERE id = 1;
-- version = 5

-- Update with version check
UPDATE products
SET price = 29.99, version = version + 1
WHERE id = 1 AND version = 5;
-- If 0 rows affected → someone else modified it → retry!
```

**Approach 2: Pessimistic Locking (SELECT FOR UPDATE)**

```sql
BEGIN;
SELECT * FROM products WHERE id = 1 FOR UPDATE;
-- Row is locked until COMMIT
UPDATE products SET price = 29.99 WHERE id = 1;
COMMIT;
```

**Approach 3: Serializable Isolation**

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- PostgreSQL detects conflicts automatically
-- Application must handle serialization errors and retry
COMMIT;
```

---

### Q4: What is `SELECT ... FOR UPDATE SKIP LOCKED` and when is it useful?

It's the foundation of a **job queue in PostgreSQL**:

```sql
-- Worker picks up next available job (skips jobs being processed by other workers)
BEGIN;
SELECT * FROM jobs
WHERE status = 'pending'
ORDER BY priority DESC, created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;

-- Process the job...
UPDATE jobs SET status = 'completed' WHERE id = ?;
COMMIT;
```

**Why it's powerful:** Multiple workers can process jobs concurrently without conflicts, without external queue systems (Redis, RabbitMQ).
