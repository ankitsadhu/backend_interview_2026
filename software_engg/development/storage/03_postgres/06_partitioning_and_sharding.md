# Partitioning & Sharding in PostgreSQL

## Why Partition?

When tables grow to millions/billions of rows:
- **Queries slow down** — scanning large indexes, bloated tables
- **Maintenance gets expensive** — VACUUM, REINDEX take longer
- **Archival is painful** — deleting old data generates massive WAL

Partitioning splits a **logical table** into smaller **physical sub-tables** while maintaining a single query interface.

---

## Declarative Partitioning (PostgreSQL 10+)

### Range Partitioning

Best for **time-series data** — queries filter by date range.

```sql
-- Create partitioned table
CREATE TABLE orders (
    id          bigserial,
    user_id     bigint NOT NULL,
    total       numeric(10,2) NOT NULL,
    status      text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE orders_2025_q1 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE orders_2025_q2 PARTITION OF orders
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE orders_2025_q3 PARTITION OF orders
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE orders_2025_q4 PARTITION OF orders
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
CREATE TABLE orders_2026_q1 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');

-- Default partition (catches rows that don't match any partition)
CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- Create indexes (applied to ALL partitions automatically)
CREATE INDEX idx_orders_created ON orders (created_at);
CREATE INDEX idx_orders_user ON orders (user_id);
```

> **Important:** Range bounds are **inclusive lower, exclusive upper** → `FROM ('2025-01-01') TO ('2025-04-01')` means `[Jan 1, Apr 1)`.

---

### List Partitioning

Best for **categorical data** — filter by discrete values.

```sql
CREATE TABLE customers (
    id          bigserial,
    name        text NOT NULL,
    region      text NOT NULL,
    created_at  timestamptz DEFAULT now()
) PARTITION BY LIST (region);

CREATE TABLE customers_apac PARTITION OF customers
    FOR VALUES IN ('India', 'Japan', 'Australia', 'Singapore');
CREATE TABLE customers_emea PARTITION OF customers
    FOR VALUES IN ('UK', 'Germany', 'France', 'UAE');
CREATE TABLE customers_americas PARTITION OF customers
    FOR VALUES IN ('US', 'Canada', 'Brazil', 'Mexico');
CREATE TABLE customers_default PARTITION OF customers DEFAULT;
```

---

### Hash Partitioning (PostgreSQL 11+)

Distributes data **evenly** — useful when there's no natural range/list key.

```sql
CREATE TABLE events (
    id          bigserial,
    user_id     bigint NOT NULL,
    event_type  text NOT NULL,
    payload     jsonb,
    created_at  timestamptz DEFAULT now()
) PARTITION BY HASH (user_id);

-- Create N partitions (must specify modulus and remainder)
CREATE TABLE events_p0 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE events_p2 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE events_p3 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

### Multi-Level (Sub-Partitioning)

```sql
-- First partition by range (year), then by list (region)
CREATE TABLE sales (
    id          bigserial,
    region      text NOT NULL,
    amount      numeric(10,2),
    sold_at     timestamptz NOT NULL
) PARTITION BY RANGE (sold_at);

CREATE TABLE sales_2026 PARTITION OF sales
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01')
    PARTITION BY LIST (region);

CREATE TABLE sales_2026_apac PARTITION OF sales_2026
    FOR VALUES IN ('India', 'Japan', 'Australia');
CREATE TABLE sales_2026_emea PARTITION OF sales_2026
    FOR VALUES IN ('UK', 'Germany', 'France');
```

---

## Partition Pruning

The planner **eliminates partitions** that can't contain matching rows.

```sql
-- With partition pruning, this only scans orders_2026_q1 partition
EXPLAIN SELECT * FROM orders WHERE created_at = '2026-02-15';
```

```
Append (cost=0.00..1.02 rows=1 width=52)
  ->  Seq Scan on orders_2026_q1 (cost=0.00..1.02 rows=1 width=52)
        Filter: (created_at = '2026-02-15')
```

```sql
-- Ensure partition pruning is enabled
SET enable_partition_pruning = on;  -- Default is ON

-- Runtime pruning (PostgreSQL 11+) — prunes at execution time for parameterized queries
PREPARE find_orders(timestamptz) AS
    SELECT * FROM orders WHERE created_at = $1;
EXECUTE find_orders('2026-02-15');  -- Only scans relevant partition
```

---

## Partition Maintenance

### Adding New Partitions

```sql
-- Add future partition (usually automated via cron/pg_partman)
CREATE TABLE orders_2026_q2 PARTITION OF orders
    FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
```

### Detaching and Dropping Old Partitions

```sql
-- Detach partition (fast, no data deletion)
ALTER TABLE orders DETACH PARTITION orders_2025_q1;

-- Optionally archive it
ALTER TABLE orders_2025_q1 RENAME TO orders_2025_q1_archive;

-- Or drop it entirely (instant, no VACUUM needed!)
DROP TABLE orders_2025_q1;  -- Much faster than DELETE!
```

> **Key Insight:** Dropping a partition is essentially O(1) — compared to deleting millions of rows with `DELETE` which generates WAL and dead tuples.

### pg_partman Extension

Automates partition creation and maintenance:

```sql
CREATE EXTENSION pg_partman;

SELECT create_parent(
    p_parent_table := 'public.orders',
    p_control := 'created_at',
    p_type := 'native',
    p_interval := '1 month',
    p_premake := 3  -- Pre-create 3 future partitions
);

-- Run maintenance (add to cron)
SELECT run_maintenance();
```

---

## Partitioning Constraints and Considerations

### Primary Key / Unique Constraints

```sql
-- Primary key MUST include the partition key!
CREATE TABLE orders (
    id          bigserial,
    created_at  timestamptz NOT NULL,
    total       numeric(10,2),
    PRIMARY KEY (id, created_at)   -- Must include partition key
) PARTITION BY RANGE (created_at);

-- Global unique constraint across partitions is NOT directly supported
-- Workaround: Use a unique index on partition key + unique column
```

### Foreign Keys

```sql
-- PostgreSQL 12+: Partitioned tables can be REFERENCED by foreign keys
-- PostgreSQL 11: Partitioned tables CAN reference other tables

CREATE TABLE order_items (
    id bigserial PRIMARY KEY,
    order_id bigint NOT NULL,
    order_date timestamptz NOT NULL,
    FOREIGN KEY (order_id, order_date) REFERENCES orders (id, created_at)
);
```

---

## Sharding Strategies

Sharding = distributing data across **multiple database servers** (horizontal scaling).

### Application-Level Sharding

```
Application determines which shard to query:

User ID → hash(user_id) % N → Shard #

Shard 0: PostgreSQL Server A (users 0, 4, 8, ...)
Shard 1: PostgreSQL Server B (users 1, 5, 9, ...)
Shard 2: PostgreSQL Server C (users 2, 6, 10, ...)
Shard 3: PostgreSQL Server D (users 3, 7, 11, ...)
```

**Pros:** Full control, no special tools
**Cons:** Cross-shard queries are complex, re-sharding is painful, application complexity

---

### Citus (PostgreSQL Extension)

Distributes PostgreSQL across multiple nodes transparently.

```sql
-- Distribute a table across worker nodes
SELECT create_distributed_table('orders', 'user_id');

-- Queries are automatically routed to the right shard
SELECT * FROM orders WHERE user_id = 42;  -- Sent to one shard

-- Cross-shard queries are supported (with performance cost)
SELECT user_id, SUM(total) FROM orders GROUP BY user_id;
```

**Key Concepts:**
- **Coordinator node** — receives queries, routes to workers
- **Worker nodes** — store and process data shards
- **Distribution column** — determines shard placement (choose carefully!)
- **Co-location** — tables with same distribution column are co-located for efficient joins

---

### Foreign Data Wrappers (postgres_fdw)

Query remote PostgreSQL servers as if they were local tables.

```sql
CREATE EXTENSION postgres_fdw;

CREATE SERVER remote_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'remote-host', port '5432', dbname 'remote_db');

CREATE USER MAPPING FOR current_user
    SERVER remote_server
    OPTIONS (user 'remote_user', password 'secret');

CREATE FOREIGN TABLE remote_orders (
    id bigint,
    user_id bigint,
    total numeric(10,2),
    created_at timestamptz
) SERVER remote_server OPTIONS (table_name 'orders');

-- Query remote table like a local table
SELECT * FROM remote_orders WHERE user_id = 42;
```

---

## Partitioning vs Sharding Decision Matrix

| Criterion | Partitioning | Sharding |
|-----------|-------------|----------|
| **Scale** | Single server, 100M-1B rows | Multi-server, billions+ |
| **Complexity** | Low (built-in) | High (orchestration needed) |
| **Cross-partition queries** | Transparent | Complex (cross-shard joins) |
| **Maintenance** | Standard PostgreSQL | Distributed ops |
| **When to use** | Time-series, archival, query performance | Write throughput, storage limits, geographic distribution |

---

## Common Interview Questions

### Q1: When would you use partitioning vs. indexing?

**Indexing** solves: "Find specific rows quickly"
**Partitioning** solves: "Manage large volumes of data efficiently"

Use partitioning when:
1. Table is very large (>100M rows) and queries filter on a natural partition key (date, region)
2. You need efficient archival (drop old partitions)
3. Maintenance operations (VACUUM, REINDEX) are too slow on the full table
4. You have time-series data with natural range boundaries

Use indexing alone when:
- Table is moderate size
- Queries filter on diverse columns (not a single partition key)
- Write performance is critical (partitioning adds routing overhead)

---

### Q2: What are the limitations of PostgreSQL partitioning?

1. **Primary key must include partition key** — can't have globally unique ID without partition key
2. **No global unique constraints** across partitions (without including partition key)
3. **Cross-partition queries** may be slower (must scan/join multiple partitions)
4. **`UPDATE` that changes partition key** → row moves between partitions (slower, PostgreSQL 11+)
5. **Too many partitions** degrades planning time (>1000 partitions can slow planner)
6. **Foreign keys** support was limited before PostgreSQL 12

---

### Q3: How do you choose a good shard key?

1. **High cardinality** — many distinct values (user_id ✅, status ❌)
2. **Even distribution** — data spreads evenly (avoid hotspots)
3. **Query affinity** — most queries filter on this key (avoids cross-shard queries)
4. **Co-location** — related tables share the shard key (enables local joins)
5. **Immutable** — value doesn't change (re-sharding is expensive)

**Good shard keys:** `user_id`, `tenant_id`, `organization_id`
**Bad shard keys:** `created_at` (time hotspot), `status` (low cardinality), `country` (uneven distribution)
