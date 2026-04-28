# PostgreSQL Indexing

## Why Indexes Matter

Without an index, PostgreSQL performs a **Sequential Scan** (reads every row). With the right index, it can jump directly to matching rows.

```
Without Index: O(n) — scan all rows
With B-Tree:   O(log n) — binary search through tree
```

### The Cost of Indexes

| Benefit | Cost |
|---------|------|
| Faster reads/lookups | Slower writes (INSERT/UPDATE/DELETE must maintain index) |
| Support ORDER BY, GROUP BY | Disk space usage |
| Enable index-only scans | More choices for planner (sometimes wrong choice) |
| Enforce uniqueness | Bloat over time (need REINDEX) |

---

## Index Types

### 1. B-Tree (Default)

The **default and most common** index type. Works for equality and range queries.

```sql
-- Automatically created for PRIMARY KEY and UNIQUE constraints
CREATE INDEX idx_users_email ON users (email);

-- Equivalent to:
CREATE INDEX idx_users_email ON users USING btree (email);
```

**Supports operators:** `<`, `<=`, `=`, `>=`, `>`, `BETWEEN`, `IN`, `IS NULL`, `IS NOT NULL`

**Also supports:** `LIKE 'prefix%'` (but NOT `LIKE '%suffix'`)

```
B-Tree Structure:
                    ┌───────────────┐
                    │   [M]         │        ← Root
                    └──┬─────────┬──┘
                       │         │
              ┌────────▼──┐  ┌──▼────────┐
              │ [D] [H]   │  │ [R] [W]   │  ← Internal Nodes
              └┬───┬───┬──┘  └┬───┬───┬──┘
               │   │   │      │   │   │
              ▼   ▼   ▼      ▼   ▼   ▼
           [A-C][D-G][H-L] [M-Q][R-V][W-Z]  ← Leaf Nodes (linked list)
```

**Key Properties:**
- Leaf nodes are doubly-linked → efficient range scans
- Height is typically 3-4 for millions of rows
- Each node = 8KB page (same as PostgreSQL's page size)

---

### 2. Hash Index

Only supports **equality** (`=`) comparisons. Smaller and faster than B-Tree for exact lookups.

```sql
CREATE INDEX idx_users_session ON sessions USING hash (session_token);
```

**When to use:** Exact match lookups only (e.g., session tokens, UUIDs)
**Limitation:** No range queries, no ordering, no multi-column support

> **Note:** Prior to PostgreSQL 10, hash indexes weren't WAL-logged (not crash-safe). Since PG10, they're fully durable.

---

### 3. GIN (Generalized Inverted Index)

For **values that contain multiple elements** — arrays, JSONB, full-text search.

```sql
-- JSONB containment queries
CREATE INDEX idx_products_metadata ON products USING gin (metadata);

SELECT * FROM products WHERE metadata @> '{"category": "electronics"}';
SELECT * FROM products WHERE metadata ? 'discount';

-- Array containment
CREATE INDEX idx_posts_tags ON posts USING gin (tags);
SELECT * FROM posts WHERE tags @> ARRAY['postgres'];

-- Full-text search
CREATE INDEX idx_articles_search ON articles USING gin (to_tsvector('english', body));
SELECT * FROM articles WHERE to_tsvector('english', body) @@ to_tsquery('postgres & indexing');

-- Trigram similarity (pg_trgm extension)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_users_name_trgm ON users USING gin (name gin_trgm_ops);
SELECT * FROM users WHERE name ILIKE '%alice%';  -- Now uses index!
```

**Supports:** `@>`, `<@`, `?`, `?|`, `?&`, `&&`, `@@`

**How GIN works:**
```
Document: "PostgreSQL is a powerful database"

GIN Index (inverted):
  "PostgreSQL" → [row1, row5, row12]
  "powerful"   → [row1, row3, row7]
  "database"   → [row1, row2, row4, row7, row12]
```

**Trade-offs:**
- Slower to build and update than B-Tree
- Excellent for read-heavy workloads with containment queries
- `fastupdate = on` (default) buffers insertions for batch processing

---

### 4. GiST (Generalized Search Tree)

For **geometric data, ranges, full-text search, and custom types**. Supports lossy/lossless operations.

```sql
-- Range types (overlap, containment)
CREATE INDEX idx_reservations_during ON reservations USING gist (during);
SELECT * FROM reservations WHERE during && '[2026-03-01, 2026-03-31]'::tstzrange;

-- Geometric data (PostGIS)
CREATE INDEX idx_locations_geom ON locations USING gist (geom);
SELECT * FROM locations
WHERE ST_DWithin(geom, ST_MakePoint(-73.9857, 40.7484)::geography, 1000);

-- Full-text search (alternative to GIN)
CREATE INDEX idx_articles_fts ON articles USING gist (to_tsvector('english', body));

-- Exclusion constraints
EXCLUDE USING gist (room_id WITH =, during WITH &&);
```

**GIN vs GiST for Full-Text Search:**

| | GIN | GiST |
|---|-----|------|
| Build speed | Slower | Faster |
| Lookup speed | Faster (exact) | Slower (lossy) |
| Update speed | Slower | Faster |
| Size | Larger | Smaller |
| Best for | Static data, read-heavy | Frequently updated data |

---

### 5. BRIN (Block Range Index)

For **large, naturally ordered tables** (e.g., time-series data). Extremely compact.

```sql
CREATE INDEX idx_logs_created ON logs USING brin (created_at);
```

**How BRIN works:**
```
Block 0 (pages 0-127):   min=2026-01-01, max=2026-01-15
Block 1 (pages 128-255): min=2026-01-15, max=2026-02-01
Block 2 (pages 256-383): min=2026-02-01, max=2026-02-15
...
```

- Stores min/max values per **block range** (128 pages by default)
- Tiny index size (can be 1000x smaller than B-Tree)
- Only works well when data is **physically ordered** (correlation ≈ 1.0)

```sql
-- Check correlation (how well physical order matches logical order)
SELECT tablename, attname, correlation
FROM pg_stats
WHERE tablename = 'logs'
AND attname = 'created_at';
-- correlation close to 1.0 or -1.0 = BRIN will work great
```

**Use Cases:** Time-series data, append-only logs, IoT sensor data

---

### 6. SP-GiST (Space-Partitioned GiST)

For data with **natural clustering and non-balanced tree structures**: quadtrees, k-d trees, radix trees.

```sql
-- IP address range lookups
CREATE INDEX idx_ip ON access_log USING spgist (client_ip inet_ops);

-- Text prefix operations
CREATE INDEX idx_phone ON contacts USING spgist (phone text_ops);
```

---

## Composite (Multi-Column) Indexes

```sql
CREATE INDEX idx_users_role_active ON users (role, is_active);
```

### Column Order Matters!

The **leftmost prefix rule** — the index can be used for queries that filter on:
- `role` only ✅
- `role` AND `is_active` ✅
- `is_active` only ❌ (can't skip leading column)

```sql
-- Uses the index ✅
SELECT * FROM users WHERE role = 'admin';
SELECT * FROM users WHERE role = 'admin' AND is_active = true;

-- Does NOT use the index ❌
SELECT * FROM users WHERE is_active = true;
```

### Column Order Guidelines

1. **Equality columns first**, then range columns
2. **High selectivity columns first** (more unique values)
3. Consider adding columns for **index-only scans**

```sql
-- Good: equality first, range second
CREATE INDEX idx_orders_status_date ON orders (status, created_at);

-- Query benefits from this order:
SELECT * FROM orders WHERE status = 'pending' AND created_at > '2026-01-01';
```

---

## Partial Indexes

Index only a **subset of rows**. Smaller, faster, and more targeted.

```sql
-- Only index active users (if most users are inactive)
CREATE INDEX idx_active_users ON users (email) WHERE is_active = true;

-- Only index pending orders
CREATE INDEX idx_pending_orders ON orders (created_at) WHERE status = 'pending';

-- Only index non-null values
CREATE INDEX idx_users_phone ON users (phone) WHERE phone IS NOT NULL;
```

**Benefits:** Much smaller index, faster updates, better cache hit rates.

**Query MUST include the WHERE clause** for the index to be used:
```sql
-- Uses partial index ✅
SELECT * FROM users WHERE email = 'alice@test.com' AND is_active = true;

-- Does NOT use partial index ❌
SELECT * FROM users WHERE email = 'alice@test.com';
```

---

## Covering Indexes (INCLUDE)

Add extra columns to the index **without affecting sort order**, enabling **index-only scans**.

```sql
CREATE INDEX idx_users_email_include ON users (email) INCLUDE (name, created_at);

-- This query can be served entirely from the index (no table access!)
SELECT name, created_at FROM users WHERE email = 'alice@test.com';
```

**Index-Only Scan vs Index Scan:**
```
Index-Only Scan:  Index → Result (no table access)
Index Scan:       Index → Table (heap) → Result
```

> **Important:** Index-only scans only work when the **visibility map** confirms all tuples on the page are visible. Regular `VACUUM` is essential.

---

## Expression Indexes (Functional Indexes)

Index on the **result of an expression or function**.

```sql
-- Case-insensitive email search
CREATE INDEX idx_users_email_lower ON users (lower(email));

SELECT * FROM users WHERE lower(email) = 'alice@test.com';  -- Uses index ✅
SELECT * FROM users WHERE email = 'alice@test.com';          -- Does NOT use index ❌

-- Index on JSONB field
CREATE INDEX idx_products_category ON products ((metadata->>'category'));

SELECT * FROM products WHERE metadata->>'category' = 'electronics';  -- Uses index ✅

-- Index on computed date
CREATE INDEX idx_orders_month ON orders (date_trunc('month', created_at));
```

---

## Index Maintenance

### Checking Index Usage

```sql
-- Find unused indexes
SELECT
    schemaname, tablename, indexname,
    idx_scan AS times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexrelid NOT IN (
    SELECT conindid FROM pg_constraint WHERE contype IN ('p', 'u')
)
ORDER BY pg_relation_size(indexrelid) DESC;

-- Index hit rate (should be > 99%)
SELECT
    relname,
    CASE WHEN idx_scan + seq_scan = 0 THEN 0
         ELSE round(100.0 * idx_scan / (idx_scan + seq_scan), 2)
    END AS idx_hit_pct
FROM pg_stat_user_tables
ORDER BY (idx_scan + seq_scan) DESC;
```

### Rebuilding Indexes

```sql
-- Standard rebuild (locks table)
REINDEX INDEX idx_users_email;
REINDEX TABLE users;

-- Concurrent rebuild (no lock, but slower)
REINDEX INDEX CONCURRENTLY idx_users_email;

-- Create index without locking writes
CREATE INDEX CONCURRENTLY idx_users_name ON users (name);
-- Note: CONCURRENTLY cannot run inside a transaction block
```

### Index Bloat

Over time, indexes accumulate dead entries from UPDATE/DELETE operations.

```sql
-- Check index bloat using pgstattuple extension
CREATE EXTENSION IF NOT EXISTS pgstattuple;
SELECT * FROM pgstatindex('idx_users_email');
-- Look at: avg_leaf_density (should be > 90%), leaf_pages, dead_items
```

---

## Common Interview Questions — Indexing

### Q1: When should you NOT use an index?

1. **Small tables** — Sequential scan is faster (no overhead)
2. **Low selectivity columns** — Boolean or status columns with few distinct values
3. **Write-heavy tables** — Indexes slow down INSERT/UPDATE/DELETE
4. **Columns rarely used in WHERE/JOIN/ORDER BY**
5. **Wide columns** — Large text columns bloat the index

> **Rule of thumb:** If a query returns more than ~10-15% of the table, PostgreSQL may prefer a sequential scan even with an index available.

---

### Q2: Explain the difference between Index Scan, Index-Only Scan, and Bitmap Index Scan.

| Scan Type | How It Works | When Used |
|-----------|-------------|-----------|
| **Index Scan** | Reads index → follows pointer to table → returns row | Few rows expected, data needed from table |
| **Index-Only Scan** | Reads index only, no table access | All needed columns are in the index (covering index) |
| **Bitmap Index Scan** | Reads index → builds bitmap of pages → seq scan those pages | Moderate number of rows, avoids random I/O |

```
Few rows ──────────────── Many rows
    │                        │
    ▼                        ▼
Index Scan → Bitmap Scan → Sequential Scan
```

---

### Q3: Why does `LIKE '%text%'` not use a B-Tree index? How to fix it?

B-Tree indexes only support **left-anchored** patterns (`LIKE 'prefix%'`).

**Solution — pg_trgm extension:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_name_trgm ON users USING gin (name gin_trgm_ops);

-- Now uses the GIN index!
SELECT * FROM users WHERE name ILIKE '%alice%';
```

**pg_trgm** breaks text into trigrams: `"alice"` → `{"  a", " al", "ali", "lic", "ice", "ce "}` and builds an inverted index over them.

---

### Q4: How do you decide which columns to include in a composite index?

1. **Equality conditions first**, range conditions second
2. **Most selective column first** (highest cardinality)
3. Add `INCLUDE` columns for index-only scans
4. Check the actual query patterns with `EXPLAIN ANALYZE`
5. One well-designed composite index > multiple single-column indexes

```sql
-- For query: WHERE status = 'active' AND created_at > '2026-01-01' ORDER BY created_at
-- Best index:
CREATE INDEX idx_orders_status_created ON orders (status, created_at);
-- status (equality) first, created_at (range + ORDER BY) second
```
