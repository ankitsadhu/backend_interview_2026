# Query Optimization in PostgreSQL

## Understanding EXPLAIN

`EXPLAIN` shows the **query execution plan** — how PostgreSQL plans to execute your query.

```sql
EXPLAIN SELECT * FROM users WHERE email = 'alice@test.com';
```

```
                        QUERY PLAN
------------------------------------------------------------
 Index Scan using idx_users_email on users  (cost=0.42..8.44 rows=1 width=120)
   Index Cond: (email = 'alice@test.com'::text)
```

### Reading the Output

- **`cost=0.42..8.44`** — Startup cost .. Total cost (in arbitrary units based on `seq_page_cost`)
- **`rows=1`** — Estimated number of rows returned
- **`width=120`** — Estimated average row size in bytes

### EXPLAIN vs EXPLAIN ANALYZE

| | EXPLAIN | EXPLAIN ANALYZE |
|---|---------|-----------------|
| Executes query? | No | **Yes** (actually runs it!) |
| Shows | Estimated costs/rows | Actual time, rows, loops |
| Side effects | None | Writes/deletes happen! |
| Use with DML | Safe always | Use with `BEGIN; ... ROLLBACK;` |

```sql
-- EXPLAIN ANALYZE — shows ACTUAL execution data
EXPLAIN ANALYZE SELECT * FROM users WHERE age > 25;
```

```
                                              QUERY PLAN
------------------------------------------------------------------------------------------------------
 Seq Scan on users  (cost=0.00..1693.00 rows=45231 width=120) (actual time=0.015..12.346 rows=45000 loops=1)
   Filter: (age > 25)
   Rows Removed by Filter: 5000
 Planning Time: 0.085 ms
 Execution Time: 14.234 ms
```

### EXPLAIN Options

```sql
-- Full detail
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;

-- JSON output (great for tools)
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT ...;

-- Key options:
-- ANALYZE     — Actually execute the query
-- BUFFERS     — Show buffer hit/miss statistics
-- COSTS       — Show cost estimates (default ON)
-- TIMING      — Show per-node timing (default ON with ANALYZE)
-- VERBOSE     — Show additional detail (output columns, schema names)
-- SETTINGS    — Show non-default configuration parameters
-- WAL         — Show WAL usage (for write queries)
```

### BUFFERS Output

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE id = 42;
```

```
 Index Scan using users_pkey on users  (cost=0.42..8.44 rows=1 width=120) (actual time=0.023..0.024 rows=1 loops=1)
   Index Cond: (id = 42)
   Buffers: shared hit=4          ← 4 pages found in shared buffers (cache)
                                  ← shared read=N would mean disk access
 Planning Time: 0.068 ms
 Execution Time: 0.042 ms
```

- **`shared hit`** — Pages found in shared buffers (memory cache) ✅
- **`shared read`** — Pages read from disk ❌ (slow)
- **`shared dirtied`** — Pages modified in memory
- **`shared written`** — Pages flushed to disk

---

## Scan Types

### Sequential Scan (Seq Scan)

Reads **every page** in the table sequentially.

```
Table Pages: [1][2][3][4][5][6][7][8][9][10]
Seq Scan:     →  →  →  →  →  →  →  →  →  →   (reads all)
```

**When used:** No usable index, small table, or query returns most rows.

```sql
-- Force/prevent seq scan (for testing only!)
SET enable_seqscan = off;
```

---

### Index Scan

Uses index to find **row locations (TIDs)**, then fetches rows from the table heap.

```
Index: email='alice' → (page 5, row 3)
                ↓
Table:  [1][2][3][4][5→row3][6][7]   ← Random I/O to table
```

**When used:** Few rows expected, index available on WHERE column.

---

### Index-Only Scan

Reads data **entirely from the index** — never touches the table.

```
Index: (email, name, created_at)
Query: SELECT name, created_at FROM users WHERE email = 'x';
                ↓
Index has all needed data → return directly
```

**Requirements:**
1. All queried columns must be in the index (covering index)
2. Visibility map must be up-to-date (run `VACUUM`)

---

### Bitmap Index Scan

Two-phase approach: first builds a **bitmap** of pages to visit, then reads those pages.

```
Phase 1 — Bitmap Index Scan:
  Index → Bitmap: [0][0][1][0][1][0][0][1][0][0]  (pages with matches)

Phase 2 — Bitmap Heap Scan:
  Table:  [1][2][3✓][4][5✓][6][7][8✓][9][10]  (only read marked pages)
```

**When used:** Moderate selectivity (too many rows for index scan, too few for seq scan).

**Bonus — BitmapAnd/BitmapOr:** Can combine bitmaps from **multiple indexes**!

```sql
-- PostgreSQL combines two single-column indexes
SELECT * FROM users WHERE age > 25 AND city = 'NYC';
  → BitmapAnd
      → Bitmap Index Scan on idx_users_age
      → Bitmap Index Scan on idx_users_city
```

---

## Join Algorithms

### Nested Loop Join

For **each row** in the outer table, scan the inner table.

```
For each row in users:           ← Outer
    For each row in orders:      ← Inner
        If match → output
```

**Cost:** O(n × m) without index, O(n × log m) with index on inner table.
**Best for:** Small outer table, indexed inner table.

---

### Hash Join

Build a **hash table** from the smaller relation, then probe it with the larger relation.

```
Phase 1 — Build:  Hash(small_table)  → in-memory hash table
Phase 2 — Probe:  For each row in large_table → lookup in hash table
```

**Cost:** O(n + m).
**Best for:** Large joins without usable indexes, equality joins.
**Limitation:** Only works for equality conditions (`=`), not range conditions.

---

### Merge Join

Both inputs are **sorted** on the join key, then merged in a single pass.

```
Sorted users:  [1, 2, 3, 5, 8, 13]
Sorted orders: [1, 1, 2, 3, 5, 5]
                ↓  ↓  ↓  ↓  ↓  ↓
Merge:          (1,1)(1,1)(2,2)(3,3)(5,5)(5,5)  ← Single pass
```

**Cost:** O(n log n + m log m) for sort + O(n + m) for merge.
**Best for:** Large, pre-sorted (or index-ordered) data, range joins.

### Join Algorithm Decision Matrix

| Scenario | Best Algorithm |
|----------|---------------|
| Inner table has index, few outer rows | Nested Loop |
| No indexes, equality condition | Hash Join |
| Both tables sorted or have sorted indexes | Merge Join |
| Very small outer + large inner with index | Nested Loop |
| Large unsorted tables, equality join | Hash Join |

---

## Common Query Optimization Techniques

### 1. Avoid SELECT *

```sql
-- Bad: fetches all columns, prevents index-only scans
SELECT * FROM users WHERE email = 'alice@test.com';

-- Good: fetch only what you need
SELECT id, name FROM users WHERE email = 'alice@test.com';
```

---

### 2. Use EXISTS Instead of IN for Subqueries

```sql
-- Slower with large subquery result
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE total > 100);

-- Faster: stops at first match
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.total > 100);
```

---

### 3. Avoid Functions on Indexed Columns

```sql
-- Bad: can't use index on email
SELECT * FROM users WHERE lower(email) = 'alice@test.com';

-- Fix 1: Create expression index
CREATE INDEX idx_email_lower ON users (lower(email));

-- Fix 2: Use CITEXT extension for case-insensitive text
CREATE EXTENSION IF NOT EXISTS citext;
ALTER TABLE users ALTER COLUMN email TYPE citext;
```

---

### 4. Use Proper Pagination

```sql
-- Bad: OFFSET skips rows one by one (O(n) for page n)
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 10000;
-- PostgreSQL must scan 10,020 rows and throw away 10,000

-- Good: Keyset pagination (O(log n) with index)
SELECT * FROM users
WHERE id > 10000             -- last id from previous page
ORDER BY id
LIMIT 20;
```

---

### 5. Batch Operations

```sql
-- Bad: N separate queries
INSERT INTO logs (msg) VALUES ('log1');
INSERT INTO logs (msg) VALUES ('log2');
-- ... × 1000

-- Good: Single multi-row insert
INSERT INTO logs (msg) VALUES ('log1'), ('log2'), ... ;

-- Even better: Use COPY for bulk loading
COPY logs (msg) FROM '/path/to/data.csv' WITH (FORMAT csv);
```

---

### 6. Optimize JOINs

```sql
-- Ensure join columns are indexed
CREATE INDEX idx_orders_user_id ON orders (user_id);

-- Ensure data types match (avoid implicit casts!)
-- Bad: user_id is bigint in users but integer in orders
-- This prevents index usage due to type mismatch
```

---

### 7. Use Materialized Views for Expensive Queries

```sql
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT
    date_trunc('month', created_at) AS month,
    product_id,
    SUM(quantity) AS total_qty,
    SUM(total) AS total_revenue
FROM orders
GROUP BY 1, 2;

-- Create index on materialized view
CREATE INDEX idx_monthly_sales_product ON monthly_sales (product_id, month);

-- Refresh (blocks reads during refresh)
REFRESH MATERIALIZED VIEW monthly_sales;

-- Concurrent refresh (no blocking, but needs unique index)
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;
```

---

## Statistics and the Query Planner

### How Statistics Work

PostgreSQL collects statistics about table data to make good planning decisions:

```sql
-- View statistics
SELECT
    attname,
    n_distinct,         -- Number of distinct values (-1 means unique)
    most_common_vals,   -- Most frequent values
    most_common_freqs,  -- Frequency of most common values
    histogram_bounds,   -- Distribution boundaries
    correlation         -- Physical vs logical order correlation
FROM pg_stats
WHERE tablename = 'users' AND attname = 'role';
```

### Common Statistics Issues

```sql
-- Problem 1: Stale statistics after bulk load
-- Fix: Run ANALYZE
ANALYZE users;
ANALYZE;  -- All tables

-- Problem 2: Non-uniform distribution
-- Fix: Increase statistics target
ALTER TABLE users ALTER COLUMN status SET STATISTICS 1000;
-- Default is 100, max is 10000. Higher = more accurate but slower ANALYZE

-- Problem 3: Correlated columns
-- Fix: Create extended statistics (PG 10+)
CREATE STATISTICS stat_city_country (dependencies) ON city, country FROM addresses;
ANALYZE addresses;
```

---

## Common Interview Questions — Query Optimization

### Q1: A query is slow. Walk me through how you'd diagnose it.

1. **`EXPLAIN (ANALYZE, BUFFERS)`** — Get the actual execution plan
2. **Check scan types** — Sequential scan on a large table? Missing index?
3. **Check row estimates** — If estimated rows ≠ actual rows → stale stats → run `ANALYZE`
4. **Check buffers** — Many `shared read`? → Working set doesn't fit in `shared_buffers`
5. **Check join algorithms** — Nested loop on large tables? Add index or increase `work_mem`
6. **Check for sort/hash on disk** — `Sort Method: external merge` → increase `work_mem`
7. **Check for seq scans** — Missing index or low selectivity?
8. **Check `pg_stat_user_tables`** — Table bloat? Run `VACUUM FULL`

---

### Q2: What is the difference between `work_mem` and `shared_buffers`?

| Parameter | Purpose | Scope |
|-----------|---------|-------|
| `shared_buffers` | Cache for table/index pages | **Global** (shared by all connections) |
| `work_mem` | Memory for sorts, hash joins, hash aggregates | **Per operation per connection** |

```sql
-- A complex query with 5 sort/hash operations and 100 connections:
-- Total potential work_mem usage = 5 × 100 × work_mem
-- Be careful setting this too high!

-- Typical values:
shared_buffers = '4GB'     -- 25% of total RAM
work_mem = '32MB'          -- Set conservatively, increase per-session if needed

-- Increase for specific session
SET work_mem = '256MB';
```

---

### Q3: Why might PostgreSQL choose a Sequential Scan even when an index exists?

1. **Table is small** — Seq scan is faster (no index overhead)
2. **Query returns many rows** — If returning >10-15% of table, seq scan is cheaper
3. **Stale statistics** — Planner thinks table is small or many rows match. Run `ANALYZE`
4. **`random_page_cost` too high** — On SSDs, set `random_page_cost = 1.1` (default is 4.0)
5. **Data types mismatch** — Implicit cast prevents index use
6. **Function on column** — `WHERE lower(email) = 'x'` won't use index on `email`
7. **Wrong operator** — `LIKE '%text%'` can't use B-Tree
8. **Parallel seq scan available** — Parallel workers make seq scan competitive

```sql
-- Set for SSD storage
SET random_page_cost = 1.1;  -- Default 4.0 assumes HDD
SET effective_cache_size = '12GB';  -- Total memory available for caching
```

---

### Q4: How do you identify and fix a slow query in production?

```sql
-- Step 1: Enable slow query logging
-- postgresql.conf:
log_min_duration_statement = 200   -- Log queries taking > 200ms

-- Step 2: Find slow queries via pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT
    calls,
    round(total_exec_time::numeric, 2) AS total_time_ms,
    round(mean_exec_time::numeric, 2) AS avg_time_ms,
    rows,
    query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Step 3: EXPLAIN ANALYZE the problematic query
-- Step 4: Add missing indexes, fix statistics, tune parameters
-- Step 5: Use pg_stat_user_tables to check for bloat

SELECT
    relname,
    n_tup_ins, n_tup_upd, n_tup_del,
    n_live_tup, n_dead_tup,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
    last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```
