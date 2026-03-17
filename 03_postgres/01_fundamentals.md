# PostgreSQL Fundamentals

## What is PostgreSQL?

**PostgreSQL** (often called **Postgres**) is an **open-source, object-relational database management system (ORDBMS)** known for its reliability, feature richness, and standards compliance.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **ACID Compliant** | Full transactional support with crash recovery |
| **MVCC** | Multi-Version Concurrency Control — readers never block writers |
| **Extensible** | Custom types, operators, functions, index methods, procedural languages |
| **SQL Standards** | Most standards-compliant open-source database (SQL:2016) |
| **Rich Data Types** | JSON/JSONB, arrays, hstore, ranges, geometric, network types |
| **Advanced Indexing** | B-Tree, Hash, GIN, GiST, SP-GiST, BRIN |
| **Replication** | Built-in streaming and logical replication |
| **Partitioning** | Declarative range, list, and hash partitioning |

---

## Architecture Overview

```
Client (psql, app)
      │
      ▼
┌──────────────────────────────────┐
│         Postmaster (PID 1)       │  ← Main daemon, listens on port 5432
│   Spawns one backend per client  │
└────────────┬─────────────────────┘
             │ fork()
             ▼
┌──────────────────────────────────┐
│       Backend Process            │  ← One per connection
│  ┌────────────────────────┐      │
│  │ Parser → Rewriter →    │      │
│  │ Planner → Executor     │      │
│  └────────────────────────┘      │
└────────────┬─────────────────────┘
             │ reads/writes
             ▼
┌──────────────────────────────────┐
│       Shared Memory              │
│  ┌──────────┐ ┌───────────────┐  │
│  │ Shared   │ │  WAL Buffers  │  │
│  │ Buffers  │ │               │  │
│  └──────────┘ └───────────────┘  │
│  ┌──────────┐ ┌───────────────┐  │
│  │ CLOG     │ │ Lock Tables   │  │
│  └──────────┘ └───────────────┘  │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│         Disk Storage             │
│  Data Files ┃ WAL Files ┃ CLOG  │
└──────────────────────────────────┘
```

### Key Processes

| Process | Role |
|---------|------|
| **Postmaster** | Main process, listens for connections, forks backend processes |
| **Backend** | One per client connection — handles query parsing, planning, execution |
| **WAL Writer** | Flushes WAL (Write-Ahead Log) buffers to disk |
| **Checkpointer** | Writes dirty shared buffer pages to disk periodically |
| **Autovacuum Launcher** | Spawns autovacuum workers to reclaim dead tuples |
| **Background Writer** | Writes dirty pages to disk to free shared buffers |
| **Stats Collector** | Collects table/index usage statistics for the query planner |
| **Logical Replication Launcher** | Manages logical replication workers |

### Process-Per-Connection Model

Unlike MySQL's thread-per-connection, PostgreSQL **forks a new process** for each connection.

**Implications:**
- Higher memory usage per connection (~5-10 MB each)
- Process isolation → one crash doesn't affect others
- Connection pooling (PgBouncer) is **critical** in production
- Context switching overhead at high connection counts

---

## How a Query Executes

```
SQL Query: SELECT * FROM users WHERE age > 25;
     │
     ▼
┌─────────────┐
│   Parser     │  ← Lexical analysis + syntax check → Parse Tree
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Analyzer    │  ← Semantic analysis (table/column existence) → Query Tree
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Rewriter    │  ← Apply rules (views, RLS policies) → Rewritten Query Tree
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Planner /   │  ← Cost-based optimizer → generates Execution Plan
│  Optimizer   │     Considers: indexes, join order, scan types, statistics
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Executor    │  ← Executes plan nodes, returns result tuples
└─────────────┘
```

### Cost-Based Optimizer

PostgreSQL's planner estimates cost using:
- **`seq_page_cost`** (default: 1.0) — cost of sequential disk page read
- **`random_page_cost`** (default: 4.0) — cost of random disk page read
- **`cpu_tuple_cost`** (default: 0.01) — cost of processing each row
- **`cpu_index_tuple_cost`** (default: 0.005) — cost of processing each index entry
- **Table statistics** — row count, data distribution, most common values, histograms

```sql
-- View table statistics
SELECT * FROM pg_stats WHERE tablename = 'users';

-- Update statistics manually
ANALYZE users;
```

---

## Installation & Connection

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@16

# Docker (recommended)
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  postgres:16

# Connect
psql -U postgres -h localhost

# Connection string
psql "postgresql://user:password@localhost:5432/mydb"
```

### Essential psql Commands

```sql
\l              -- List databases
\c dbname       -- Connect to database
\dt             -- List tables
\dt+            -- List tables with sizes
\d tablename    -- Describe table structure
\di             -- List indexes
\df             -- List functions
\du             -- List roles/users
\x              -- Toggle expanded display
\timing         -- Toggle query timing
\e              -- Open query in editor
\i file.sql     -- Execute SQL file
\q              -- Quit
```

---

## Core Data Types

### 1. Numeric Types

```sql
-- Integer types
smallint          -- 2 bytes, -32768 to +32767
integer (int)     -- 4 bytes, -2.1B to +2.1B
bigint            -- 8 bytes, -9.2 quintillion to +9.2 quintillion
serial            -- Auto-incrementing integer (4 bytes)
bigserial         -- Auto-incrementing bigint (8 bytes)

-- Exact precision
numeric(10, 2)    -- 10 total digits, 2 decimal places (for money!)
decimal(10, 2)    -- Alias for numeric

-- Floating point (avoid for money!)
real              -- 4 bytes, 6 decimal digits precision
double precision  -- 8 bytes, 15 decimal digits precision
```

> **Interview Tip:** Never use `float` or `double precision` for money.  Use `numeric` or store values in cents as `bigint`.

---

### 2. Character Types

```sql
char(n)           -- Fixed-length, padded with spaces (rarely used)
varchar(n)        -- Variable-length with limit
varchar           -- Variable-length, no limit (same as text internally)
text              -- Variable-length, unlimited

-- In PostgreSQL, there is NO performance difference between varchar and text.
-- varchar(n) only adds a length CHECK constraint.
```

> **Interview Tip:** `text` and `varchar` are stored identically in PostgreSQL. Using `varchar(255)` has **no performance benefit** — it's a MySQL habit that doesn't apply here.

---

### 3. Date/Time Types

```sql
date                -- Date only (4 bytes): '2026-03-16'
time                -- Time only (8 bytes): '14:30:00'
time with time zone -- Time + TZ: '14:30:00+05:30'
timestamp           -- Date + time (8 bytes): '2026-03-16 14:30:00'
timestamptz         -- Date + time + timezone (8 bytes, RECOMMENDED)
interval            -- Duration: '1 year 2 months 3 days'

-- Always use timestamptz!
CREATE TABLE events (
    created_at timestamptz DEFAULT now()
);

-- Interval arithmetic
SELECT now() + interval '30 days';
SELECT age(timestamp '2026-03-16', timestamp '1995-01-01');
-- Result: '31 years 2 mons 15 days'
```

> **Interview Tip:** Always use `timestamptz` instead of `timestamp`. PostgreSQL stores `timestamptz` as UTC internally and converts to the session timezone on display.

---

### 4. Boolean

```sql
boolean    -- true, false, null

-- Valid true values:  true, 't', 'yes', 'y', 'on', '1'
-- Valid false values: false, 'f', 'no', 'n', 'off', '0'
```

---

### 5. UUID

```sql
uuid       -- 128-bit universally unique identifier

-- Generate UUIDs (PostgreSQL 13+)
SELECT gen_random_uuid();
-- Result: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid()
);
```

> **Interview Tip:** UUIDs vs serial IDs — UUIDs avoid sequential scanning attacks, work across distributed systems, but are **larger (16 bytes vs 4 bytes)** and can fragment B-Tree indexes. Consider ULIDs or UUIDv7 for time-ordered inserts.

---

### 6. JSON / JSONB

```sql
json       -- Stores exact text (preserves whitespace, duplicate keys, order)
jsonb      -- Binary representation (faster queries, supports indexing)

-- Always prefer JSONB unless you need to preserve formatting.
CREATE TABLE products (
    id serial PRIMARY KEY,
    metadata jsonb
);

INSERT INTO products (metadata) VALUES
('{"name": "Widget", "tags": ["sale", "new"], "price": 29.99}');

-- Access operators
SELECT metadata->>'name' FROM products;            -- 'Widget' (as text)
SELECT metadata->'tags'->0 FROM products;           -- '"sale"' (as json)
SELECT metadata->'price' FROM products;             -- 29.99 (as json)
SELECT metadata#>>'{tags,0}' FROM products;         -- 'sale' (path as text)

-- Containment
SELECT * FROM products WHERE metadata @> '{"name": "Widget"}';

-- Existence
SELECT * FROM products WHERE metadata ? 'tags';      -- Has key 'tags'?
SELECT * FROM products WHERE metadata ?| array['a','name']; -- Has ANY of these keys?
SELECT * FROM products WHERE metadata ?& array['name','price']; -- Has ALL keys?

-- Modify JSONB
UPDATE products SET metadata = metadata || '{"stock": 100}';
UPDATE products SET metadata = metadata - 'stock';  -- Remove key
UPDATE products SET metadata = jsonb_set(metadata, '{price}', '39.99');
```

---

### 7. Arrays

```sql
-- Array column
CREATE TABLE posts (
    id serial PRIMARY KEY,
    title text,
    tags text[]      -- Array of text
);

INSERT INTO posts (title, tags) VALUES
('Postgres Tips', ARRAY['database', 'sql', 'postgres']),
('Redis Guide', '{"cache", "nosql"}');  -- Alternative syntax

-- Query arrays
SELECT * FROM posts WHERE 'sql' = ANY(tags);        -- Contains 'sql'?
SELECT * FROM posts WHERE tags @> ARRAY['sql'];     -- Contains subset?
SELECT * FROM posts WHERE tags && ARRAY['sql','cache']; -- Overlap?

-- Array functions
SELECT array_length(tags, 1) FROM posts;
SELECT unnest(tags) FROM posts;                     -- Expand to rows
SELECT array_agg(title) FROM posts;                 -- Rows to array
```

---

### 8. Other Notable Types

```sql
-- Network types
inet              -- IPv4/IPv6 host address: '192.168.1.1/24'
cidr              -- IPv4/IPv6 network: '192.168.1.0/24'
macaddr           -- MAC address: '08:00:2b:01:02:03'

-- Range types
int4range         -- Range of integers: '[1,10)'
tstzrange         -- Range of timestamptz: '[2026-01-01, 2026-12-31]'

-- Geometric types
point, line, circle, polygon, box, path

-- Binary
bytea             -- Binary string / byte array

-- Enumerated types
CREATE TYPE mood AS ENUM ('happy', 'sad', 'neutral');
CREATE TABLE people (name text, current_mood mood);
INSERT INTO people VALUES ('Alice', 'happy');
```

---

## DDL — Tables, Constraints, Schemas

### Creating Tables

```sql
CREATE TABLE users (
    id          bigserial PRIMARY KEY,
    email       text NOT NULL UNIQUE,
    name        varchar(100) NOT NULL,
    age         integer CHECK (age >= 0 AND age <= 150),
    role        text DEFAULT 'user',
    is_active   boolean DEFAULT true,
    metadata    jsonb DEFAULT '{}',
    created_at  timestamptz DEFAULT now(),
    updated_at  timestamptz DEFAULT now()
);
```

### Constraints

```sql
-- Primary Key
id bigserial PRIMARY KEY
-- or
CONSTRAINT pk_users PRIMARY KEY (id)

-- Foreign Key
CREATE TABLE orders (
    id bigserial PRIMARY KEY,
    user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total numeric(10,2) NOT NULL
);
-- ON DELETE options: CASCADE, SET NULL, SET DEFAULT, RESTRICT, NO ACTION

-- Unique
email text UNIQUE
-- or multi-column
CONSTRAINT uq_tenant_email UNIQUE (tenant_id, email)

-- Check
CHECK (price > 0)
CHECK (start_date < end_date)

-- Not Null
name text NOT NULL

-- Exclusion (advanced — prevents overlapping ranges)
CREATE TABLE reservations (
    room_id int,
    during tstzrange,
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);
-- No two rows can have same room_id AND overlapping time ranges!
```

### Schemas

```sql
-- Schemas = namespaces within a database
CREATE SCHEMA billing;

CREATE TABLE billing.invoices (
    id bigserial PRIMARY KEY,
    amount numeric(10,2)
);

-- Search path (schema resolution order)
SHOW search_path;                    -- "$user", public
SET search_path TO billing, public;

-- Multi-tenant isolation via schemas
CREATE SCHEMA tenant_abc;
CREATE TABLE tenant_abc.users (...);
```

---

## DML — CRUD Operations

### INSERT

```sql
-- Single row
INSERT INTO users (email, name, age)
VALUES ('alice@example.com', 'Alice', 30);

-- Multiple rows
INSERT INTO users (email, name, age) VALUES
    ('bob@example.com', 'Bob', 25),
    ('charlie@example.com', 'Charlie', 35);

-- Insert with RETURNING (get back inserted data)
INSERT INTO users (email, name, age)
VALUES ('dave@example.com', 'Dave', 28)
RETURNING id, email, created_at;

-- Insert from SELECT
INSERT INTO archive_users (id, email, name)
SELECT id, email, name FROM users WHERE is_active = false;

-- UPSERT (Insert or Update on conflict)
INSERT INTO users (email, name, age)
VALUES ('alice@example.com', 'Alice Updated', 31)
ON CONFLICT (email) DO UPDATE
SET name = EXCLUDED.name, age = EXCLUDED.age, updated_at = now();

-- UPSERT — do nothing on conflict
INSERT INTO users (email, name, age)
VALUES ('alice@example.com', 'Alice', 30)
ON CONFLICT (email) DO NOTHING;
```

### SELECT

```sql
-- Basic queries
SELECT * FROM users WHERE age > 25;
SELECT name, email FROM users WHERE is_active = true ORDER BY name;
SELECT DISTINCT role FROM users;

-- Pagination
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 40;  -- Page 3

-- Keyset pagination (much better for large tables!)
SELECT * FROM users
WHERE id > 1000          -- last seen id
ORDER BY id
LIMIT 20;

-- Aggregate functions
SELECT role, COUNT(*), AVG(age), MIN(age), MAX(age)
FROM users
GROUP BY role
HAVING COUNT(*) > 5;

-- String functions
SELECT
    upper(name),
    lower(email),
    length(name),
    substring(email FROM '@(.+)$') AS domain,
    concat(name, ' <', email, '>') AS formatted
FROM users;
```

### UPDATE

```sql
-- Basic update
UPDATE users SET age = 31 WHERE email = 'alice@example.com';

-- Update multiple columns
UPDATE users
SET name = 'Alice Smith', updated_at = now()
WHERE id = 1;

-- Update with RETURNING
UPDATE users SET is_active = false
WHERE last_login < now() - interval '1 year'
RETURNING id, email;

-- Update with subquery
UPDATE orders
SET status = 'cancelled'
WHERE user_id IN (SELECT id FROM users WHERE is_active = false);

-- Update with FROM (join update)
UPDATE orders o
SET status = 'vip_order'
FROM users u
WHERE o.user_id = u.id AND u.role = 'vip';
```

### DELETE

```sql
-- Basic delete
DELETE FROM users WHERE id = 42;

-- Delete with RETURNING
DELETE FROM sessions
WHERE expires_at < now()
RETURNING user_id, session_id;

-- Truncate (fast, but no row-level triggers, not MVCC-safe)
TRUNCATE TABLE logs;
TRUNCATE TABLE orders, order_items CASCADE;  -- Cascades to FK references
```

---

## Joins

```sql
-- Sample data
-- users: id, name
-- orders: id, user_id, total

-- INNER JOIN (only matching rows)
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN (all users, even without orders)
SELECT u.name, COALESCE(o.total, 0) AS total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- RIGHT JOIN (all orders, even orphaned — rare)
SELECT u.name, o.total
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- FULL OUTER JOIN (all from both sides)
SELECT u.name, o.total
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;

-- CROSS JOIN (Cartesian product)
SELECT u.name, p.product_name
FROM users u
CROSS JOIN products p;

-- Self join
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Multiple joins
SELECT u.name, o.id AS order_id, p.product_name, oi.quantity
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```

---

## Common Interview Questions — Beginner

### Q1: What is the difference between PostgreSQL and MySQL?

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Model | Object-Relational | Relational |
| ACID | Full ACID by default | InnoDB only (not MyISAM) |
| MVCC | Native, built-in | InnoDB implementation |
| JSON Support | JSONB with indexing | JSON (limited indexing) |
| Full-Text Search | Built-in `tsvector/tsquery` | Built-in but simpler |
| CTE / Window Functions | Full support since v8.4 | Added in MySQL 8.0 |
| Partitioning | Declarative (range, list, hash) | Range, list, hash, key |
| Replication | Streaming + logical | Binary log-based |
| Extensions | Rich ecosystem (PostGIS, pg_trgm, etc.) | Plugin architecture |
| Concurrency | Process-per-connection | Thread-per-connection |
| Standards | Most SQL-compliant | Some proprietary syntax |

**When to use PostgreSQL:** Complex queries, JSONB, GIS, strict data integrity, advanced features.
**When to use MySQL:** Simple read-heavy workloads, widespread hosting support, existing MySQL expertise.

---

### Q2: Explain the PostgreSQL process architecture.

PostgreSQL uses a **multi-process architecture** (not multi-threaded):

1. **Postmaster** — Main daemon that listens for connections on port 5432
2. **Backend processes** — One forked per client connection; handles parsing, planning, executing queries
3. **Background workers** — Autovacuum, WAL writer, checkpointer, stats collector, background writer

**Key difference from MySQL:** MySQL uses threads (lightweight), PostgreSQL uses processes (heavier but more isolated).

**Why processes?** Historical design choice for stability — a buggy query crashing one backend doesn't take down the server.

**Trade-off:** Higher memory usage (~5-10 MB per connection), making connection pooling (PgBouncer) essential.

---

### Q3: What is `RETURNING` clause and why is it powerful?

`RETURNING` lets you get back data from `INSERT`, `UPDATE`, or `DELETE` operations **in a single round-trip**:

```sql
-- Insert and get the auto-generated ID
INSERT INTO users (name, email) VALUES ('Alice', 'alice@test.com')
RETURNING id;

-- Update and see what changed
UPDATE products SET price = price * 1.1
WHERE category = 'electronics'
RETURNING id, name, price;

-- Delete and log what was removed
DELETE FROM expired_sessions WHERE expires < now()
RETURNING session_id, user_id;
```

**Why it matters:** Eliminates the need for a second query to fetch the data you just modified. Reduces round-trips, prevents race conditions.

---

### Q4: What is the difference between `DELETE` and `TRUNCATE`?

| Feature | DELETE | TRUNCATE |
|---------|--------|----------|
| Speed | Slow (row by row) | Fast (deallocates pages) |
| WHERE clause | Yes | No (deletes all rows) |
| MVCC safe | Yes (other transactions still see rows) | No (immediate) |
| Triggers | Fires row-level triggers | Fires statement-level triggers only |
| RETURNING | Supported | Not supported |
| Transaction | Fully transactional, can rollback | Transactional in PostgreSQL (can rollback!) |
| WAL | Generates lots of WAL | Minimal WAL |
| Vacuum needed | Yes (dead tuples remain) | No (pages freed immediately) |

> **Interview Tip:** Unlike MySQL, `TRUNCATE` in PostgreSQL **is transactional** and can be rolled back.
