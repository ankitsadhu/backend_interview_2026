# PostgreSQL Joins — Deep Dive

## How Joins Work Conceptually

A join combines rows from two or more tables based on a **related column**. Under the hood, the planner picks one of three physical algorithms (Nested Loop, Hash Join, Merge Join) based on cost estimates.

```
Table A (users)         Table B (orders)
┌────┬────────┐         ┌────┬─────────┬───────┐
│ id │ name   │         │ id │ user_id │ total │
├────┼────────┤         ├────┼─────────┼───────┤
│  1 │ Alice  │         │ 10 │    1    │  200  │
│  2 │ Bob    │         │ 11 │    1    │  150  │
│  3 │ Carol  │         │ 12 │    2    │  300  │
│  4 │ Dave   │         │ 13 │   99    │   50  │ ← orphan (no user 99)
└────┴────────┘         └────┴─────────┴───────┘
```

---

## INNER JOIN

Returns **only rows that match** in both tables. Non-matching rows are excluded.

```sql
SELECT u.name, o.id AS order_id, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

```
Result:
┌───────┬──────────┬───────┐
│ name  │ order_id │ total │
├───────┼──────────┼───────┤
│ Alice │    10    │  200  │
│ Alice │    11    │  150  │
│ Bob   │    12    │  300  │
└───────┴──────────┴───────┘
-- Carol (no orders) → excluded
-- Dave (no orders) → excluded
-- Order 13 (user 99 doesn't exist) → excluded
```

```
Venn Diagram:
  ┌───────────┐   ┌───────────┐
  │   Users   │   │  Orders   │
  │      ┌────┼───┼────┐      │
  │      │████│   │████│      │
  │      │████│   │████│      │
  │      └────┼───┼────┘      │
  └───────────┘   └───────────┘
         ████ = INNER JOIN result
```

> `JOIN` is shorthand for `INNER JOIN` — both are identical.

---

## LEFT JOIN (LEFT OUTER JOIN)

Returns **all rows from the left table**, plus matching rows from the right table. Non-matching right side produces NULLs.

```sql
SELECT u.name, o.id AS order_id, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

```
Result:
┌───────┬──────────┬───────┐
│ name  │ order_id │ total │
├───────┼──────────┼───────┤
│ Alice │    10    │  200  │
│ Alice │    11    │  150  │
│ Bob   │    12    │  300  │
│ Carol │   NULL   │  NULL │  ← No matching orders
│ Dave  │   NULL   │  NULL │  ← No matching orders
└───────┴──────────┴───────┘
```

### Find Rows WITHOUT a Match (Anti-Join)

```sql
-- Users with NO orders
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;

-- Result: Carol, Dave
```

```
Venn Diagram:
  ┌───────────┐   ┌───────────┐
  │   Users   │   │  Orders   │
  │ ████┌────┼───┼────┐      │
  │ ████│    │   │    │      │
  │ ████│    │   │    │      │
  │ ████└────┼───┼────┘      │
  └───────────┘   └───────────┘
    ████ = LEFT JOIN WHERE right IS NULL (anti-join)
```

---

## RIGHT JOIN (RIGHT OUTER JOIN)

Returns **all rows from the right table**, plus matching rows from the left table. Rarely used — a LEFT JOIN with swapped tables is more readable.

```sql
SELECT u.name, o.id AS order_id, o.total
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

```
Result:
┌───────┬──────────┬───────┐
│ name  │ order_id │ total │
├───────┼──────────┼───────┤
│ Alice │    10    │  200  │
│ Alice │    11    │  150  │
│ Bob   │    12    │  300  │
│ NULL  │    13    │   50  │  ← Order 13 has no matching user
└───────┴──────────┴───────┘
```

> **Tip:** This is equivalent to: `FROM orders o LEFT JOIN users u ON u.id = o.user_id`

---

## FULL OUTER JOIN

Returns **all rows from both tables**. NULLs fill in where no match exists on either side.

```sql
SELECT u.name, o.id AS order_id, o.total
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;
```

```
Result:
┌───────┬──────────┬───────┐
│ name  │ order_id │ total │
├───────┼──────────┼───────┤
│ Alice │    10    │  200  │
│ Alice │    11    │  150  │
│ Bob   │    12    │  300  │
│ Carol │   NULL   │  NULL │  ← User with no orders
│ Dave  │   NULL   │  NULL │  ← User with no orders
│ NULL  │    13    │   50  │  ← Order with no user
└───────┴──────────┴───────┘
```

### Find Unmatched Rows from BOTH Sides

```sql
-- Orphans on both sides
SELECT u.name, o.id AS order_id
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id
WHERE u.id IS NULL OR o.id IS NULL;
-- Carol (no orders), Dave (no orders), Order 13 (no user)
```

---

## CROSS JOIN (Cartesian Product)

Every row from the left table paired with **every row** from the right table. No `ON` clause.

```sql
SELECT u.name, p.product_name
FROM users u
CROSS JOIN products p;

-- If users has 4 rows and products has 3 rows → result has 12 rows
```

```
Result: Every combination
┌───────┬──────────────┐
│ name  │ product_name │
├───────┼──────────────┤
│ Alice │ Widget       │
│ Alice │ Gadget       │
│ Alice │ Gizmo        │
│ Bob   │ Widget       │
│ Bob   │ Gadget       │
│ Bob   │ Gizmo        │
│ Carol │ Widget       │
│  ...  │    ...       │
└───────┴──────────────┘
```

### Practical Use Cases

```sql
-- Generate all date × product combinations (fill gaps in reports)
SELECT d.date, p.product_id, COALESCE(s.quantity, 0) AS sold
FROM generate_series('2026-01-01'::date, '2026-01-31'::date, '1 day') d(date)
CROSS JOIN products p
LEFT JOIN sales s ON s.product_id = p.product_id
                 AND s.sale_date = d.date;

-- Generate a multiplication table
SELECT a.n AS x, b.n AS y, a.n * b.n AS product
FROM generate_series(1,10) a(n)
CROSS JOIN generate_series(1,10) b(n);
```

> ⚠️ **Warning:** Cross joins can produce enormous result sets. 10K × 10K = 100 million rows!

---

## Self Join

A table joined with **itself**. Always requires aliases.

```sql
-- Employee → Manager hierarchy
SELECT
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

```
Result:
┌──────────┬─────────┐
│ employee │ manager │
├──────────┼─────────┤
│ Alice    │ NULL    │  ← CEO (no manager)
│ Bob      │ Alice   │
│ Carol    │ Alice   │
│ Dave     │ Bob     │
└──────────┴─────────┘
```

### Other Self Join Use Cases

```sql
-- Find duplicate emails
SELECT a.id, a.email
FROM users a
JOIN users b ON a.email = b.email AND a.id < b.id;

-- Compare consecutive rows (alternative to LAG)
SELECT
    curr.date, curr.revenue,
    prev.revenue AS prev_revenue,
    curr.revenue - prev.revenue AS change
FROM daily_sales curr
JOIN daily_sales prev ON curr.date = prev.date + interval '1 day';

-- Find pairs of users in the same city
SELECT a.name, b.name, a.city
FROM users a
JOIN users b ON a.city = b.city AND a.id < b.id;
```

---

## NATURAL JOIN

Automatically joins on **all columns with the same name** in both tables. Generally **discouraged** — it's fragile.

```sql
-- If users has (id, name) and orders has (id, user_id, total):
SELECT * FROM users NATURAL JOIN orders;
-- Joins on "id" column (both tables have "id") — probably WRONG!
-- Intended: users.id = orders.user_id (but NATURAL picked id = id)
```

> **Avoid NATURAL JOIN** — adding a column to either table can silently change join behavior.

---

## USING Clause

A shorthand when the join column has the **same name** in both tables.

```sql
-- Instead of:
SELECT * FROM orders JOIN users ON orders.user_id = users.user_id;

-- Use:
SELECT * FROM orders JOIN users USING (user_id);
-- Note: USING produces a single "user_id" column in the result,
-- while ON produces two (orders.user_id and users.user_id)
```

---

## LATERAL JOIN

Allows a subquery in FROM to **reference columns** from preceding tables. Like a correlated subquery, but in the FROM clause.

```sql
-- Top 3 orders per user (can't do this with a regular JOIN)
SELECT u.name, latest.order_id, latest.total
FROM users u
CROSS JOIN LATERAL (
    SELECT o.id AS order_id, o.total
    FROM orders o
    WHERE o.user_id = u.id          -- References u.id!
    ORDER BY o.created_at DESC
    LIMIT 3
) latest;

-- LEFT JOIN LATERAL: include users even if they have 0 orders
SELECT u.name, latest.order_id, latest.total
FROM users u
LEFT JOIN LATERAL (
    SELECT o.id AS order_id, o.total
    FROM orders o
    WHERE o.user_id = u.id
    ORDER BY o.total DESC
    LIMIT 3
) latest ON true;                   -- ON true because condition is in subquery
```

### LATERAL vs Window Functions

```sql
-- Window function approach (all orders loaded, then filtered):
SELECT name, order_id, total FROM (
    SELECT u.name, o.id AS order_id, o.total,
        ROW_NUMBER() OVER (PARTITION BY u.id ORDER BY o.total DESC) AS rn
    FROM users u JOIN orders o ON u.id = o.user_id
) sub WHERE rn <= 3;

-- LATERAL approach (stops at LIMIT per user — often faster):
SELECT u.name, lat.order_id, lat.total
FROM users u
CROSS JOIN LATERAL (
    SELECT o.id AS order_id, o.total
    FROM orders o WHERE o.user_id = u.id
    ORDER BY o.total DESC LIMIT 3
) lat;
```

**When LATERAL wins:** Small LIMIT per row, indexed inner table, many groups.
**When window functions win:** No LIMIT needed, need rank/row_number in output, complex frames.

---

## Join Algorithms Under the Hood

PostgreSQL picks one of three physical algorithms for each join:

### 1. Nested Loop

```
For each row in Outer (users):
    For each row in Inner (orders):
        If users.id = orders.user_id → emit
```

| Aspect | Detail |
|--------|--------|
| **Cost** | O(n × m) without index, O(n × log m) with index |
| **Best when** | Small outer table, indexed inner table |
| **Supports** | All join types, all operators |
| **EXPLAIN** | `Nested Loop` |

---

### 2. Hash Join

```
Phase 1 — Build:  Read smaller table → build in-memory hash table on join key
Phase 2 — Probe:  Read larger table → probe hash table for matches
```

| Aspect | Detail |
|--------|--------|
| **Cost** | O(n + m) |
| **Best when** | No useful index, equality join, large tables |
| **Limitation** | Equality only (`=`), needs work_mem for hash table |
| **EXPLAIN** | `Hash Join` → `Hash` |

```sql
-- If hash table doesn't fit in work_mem → spills to disk "batches"
-- EXPLAIN shows: "Batches: 4  Memory Usage: 2048kB"
-- Fix: increase work_mem
SET work_mem = '128MB';
```

---

### 3. Merge Join

```
Step 1: Sort both inputs on join key (or use index order)
Step 2: Walk through both sorted lists simultaneously
```

| Aspect | Detail |
|--------|--------|
| **Cost** | O(n log n + m log m + n + m) |
| **Best when** | Both inputs already sorted (indexes!), large tables |
| **Supports** | Equality, range, and inequality operators |
| **EXPLAIN** | `Merge Join` → `Sort` |

---

### Algorithm Selection Summary

```
                          ┌──────────────────────┐
                          │    Join Required      │
                          └──────────┬───────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
              Small outer +    No index +        Both sorted /
              indexed inner    large tables       indexed
                    │                │                │
                    ▼                ▼                ▼
             Nested Loop         Hash Join       Merge Join
```

```sql
-- Force a specific join algorithm (for testing only!)
SET enable_hashjoin = off;
SET enable_mergejoin = off;
SET enable_nestloop = off;  -- Forces the remaining algorithm
```

---

## Multi-Table Joins

### Join Order Matters

The planner considers **all possible join orders** and picks the cheapest. For complex queries with many tables, this can be expensive.

```sql
-- 6-table join
SELECT c.name, o.id, oi.quantity, p.product_name, cat.category, w.warehouse
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
JOIN categories cat ON p.category_id = cat.id
JOIN warehouses w ON oi.warehouse_id = w.id
WHERE o.created_at > '2026-01-01'
  AND cat.category = 'Electronics';
```

```sql
-- For queries with many tables (12+), the planner uses GEQO (Genetic Query Optimizer)
-- Threshold is configurable:
SET geqo_threshold = 12;   -- Default: 12 tables before switching to GEQO
```

### Ensure Join Columns Are Indexed

```sql
-- Create indexes on foreign key columns (PostgreSQL doesn't auto-create these!)
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_order_items_order_id ON order_items (order_id);
CREATE INDEX idx_order_items_product_id ON order_items (product_id);
CREATE INDEX idx_products_category_id ON products (category_id);
```

> ⚠️ PostgreSQL automatically creates indexes for PRIMARY KEY and UNIQUE constraints, but **NOT for foreign keys**. Always create FK indexes manually!

---

## Join Performance Tips

### 1. Index Foreign Key Columns

```sql
-- Every FK should have an index on the referencing column
ALTER TABLE orders ADD CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id);
CREATE INDEX idx_orders_user_id ON orders (user_id);  -- MUST do this manually!
```

### 2. Avoid Type Mismatches

```sql
-- BAD: implicit cast prevents index use
-- users.id is bigint, orders.user_id is integer
SELECT * FROM users u JOIN orders o ON u.id = o.user_id;
-- PostgreSQL casts integer → bigint, but may not use index on orders.user_id!

-- FIX: Ensure matching types
ALTER TABLE orders ALTER COLUMN user_id TYPE bigint;
```

### 3. Filter Early

```sql
-- BAD: join first, filter later
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.created_at > '2026-01-01' AND u.is_active = true;
-- PostgreSQL usually optimizes this, but help it with WHERE placement

-- GOOD: same query — PostgreSQL's optimizer handles this equivalently,
-- but if using subqueries, pre-filter:
SELECT u.name, recent.total
FROM users u
JOIN (
    SELECT user_id, total FROM orders WHERE created_at > '2026-01-01'
) recent ON u.id = recent.user_id
WHERE u.is_active = true;
```

### 4. Use EXISTS Instead of JOIN for Existence Checks

```sql
-- If you only need to know IF a related row exists (not its data):

-- Slower: JOIN returns all matching rows, COUNT discards them
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.name
HAVING COUNT(o.id) > 0;

-- Faster: EXISTS stops at first match
SELECT u.name
FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

### 5. Use DISTINCT ON for "Latest Per Group"

```sql
-- Instead of complex join + window function:
SELECT DISTINCT ON (user_id)
    user_id, id AS order_id, total, created_at
FROM orders
ORDER BY user_id, created_at DESC;
-- Returns the latest order per user — clean and efficient
```

---

## Common Interview Questions — Joins

### Q1: What is the difference between WHERE and ON in joins?

**For INNER JOIN:** No difference — both filter the same way.

**For OUTER JOIN:** **Critical difference!**

```sql
-- ON: applied DURING the join (affects which rows match)
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id AND o.total > 200;
-- Returns ALL users. Orders ≤ 200 get NULL (not excluded).

-- WHERE: applied AFTER the join (filters the result)
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.total > 200;
-- Excludes users with no orders or orders ≤ 200!
-- This effectively becomes an INNER JOIN.
```

```
ON filter (LEFT JOIN preserved):
Alice  │  200         ← matches
Alice  │  NULL        ← order 11 (150) didn't match ON, but Alice kept
Bob    │  300         ← matches
Carol  │  NULL        ← no orders, kept
Dave   │  NULL        ← no orders, kept

WHERE filter (LEFT JOIN broken):
Alice  │  200         ← matches
Bob    │  300         ← matches
-- Carol, Dave eliminated by WHERE o.total > 200 (their NULL fails)
```

---

### Q2: How do you find rows that exist in one table but NOT in another?

Three approaches — all give the same result, different performance profiles:

```sql
-- Method 1: LEFT JOIN + IS NULL (most common, usually fastest)
SELECT u.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;

-- Method 2: NOT EXISTS (often equivalent performance to LEFT JOIN)
SELECT u.*
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Method 3: NOT IN (AVOID — NULL handling is tricky!)
SELECT u.*
FROM users u
WHERE u.id NOT IN (SELECT user_id FROM orders);
-- ⚠️ If orders.user_id has ANY NULLs, this returns ZERO rows!
-- Because: x NOT IN (..., NULL) is UNKNOWN for any x
```

**Best practice:** Use `LEFT JOIN ... IS NULL` or `NOT EXISTS`. Avoid `NOT IN` with nullable columns.

---

### Q3: Explain the performance difference between these join approaches for "users with orders":

```sql
-- Approach A: JOIN
SELECT DISTINCT u.* FROM users u JOIN orders o ON u.id = o.user_id;

-- Approach B: IN
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- Approach C: EXISTS
SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

| Approach | Behavior | Performance |
|----------|----------|-------------|
| **JOIN** | Joins ALL orders, then deduplicates with DISTINCT | Slow if users have many orders (many duplicates) |
| **IN** | Builds hash of order user_ids, probes | Good for small subquery results |
| **EXISTS** | Stops at first matching order per user | Best — short-circuits early |

> **PostgreSQL's optimizer** often converts IN to a semi-join (equivalent to EXISTS), but EXISTS explicitly communicates intent and is never worse.

---

### Q4: Write a query to find users who have ordered EVERY product.

This is a **relational division** problem:

```sql
-- Users who ordered every product
SELECT u.name
FROM users u
WHERE NOT EXISTS (
    -- Find a product that this user has NOT ordered
    SELECT p.id
    FROM products p
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.user_id = u.id AND oi.product_id = p.id
    )
);

-- Alternative using COUNT:
SELECT u.name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
GROUP BY u.name
HAVING COUNT(DISTINCT oi.product_id) = (SELECT COUNT(*) FROM products);
```

---

### Q5: What is a semi-join and an anti-join?

These are **logical join types** — PostgreSQL implements them but SQL has no explicit syntax for them.

| Type | SQL Pattern | Behavior |
|------|-------------|----------|
| **Semi-join** | `WHERE EXISTS (...)` or `WHERE IN (...)` | Returns left row if ANY match exists (no duplicates) |
| **Anti-join** | `WHERE NOT EXISTS (...)` or `LEFT JOIN ... IS NULL` | Returns left row if NO match exists |

```sql
-- Semi-join: "Users who have at least one order"
SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
-- Each user appears AT MOST once, even if they have 100 orders

-- Anti-join: "Users who have zero orders"
SELECT * FROM users u WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

In `EXPLAIN`, look for `Semi Join` or `Anti Join` nodes.

---

### Q6: What are the common join mistakes to avoid?

1. **Missing indexes on FK columns** — Every foreign key column needs an index
2. **Type mismatches** — Implicit casts break index usage
3. **Accidental Cartesian product** — Missing or wrong ON clause
4. **Using LEFT JOIN when INNER JOIN is intended** — Unneeded NULLs
5. **WHERE clause on outer table nullifying LEFT JOIN** — Turns it into INNER JOIN
6. **NOT IN with nullable columns** — Returns empty result if any NULL exists
7. **Joining large tables without filters** — Always push WHERE conditions early
8. **SELECT * in multi-table joins** — Fetches columns you don't need, prevents index-only scans
