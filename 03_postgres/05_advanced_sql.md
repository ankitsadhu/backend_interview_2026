# Advanced SQL in PostgreSQL

## Common Table Expressions (CTEs)

CTEs provide **named temporary result sets** within a query. Think of them as inline views.

```sql
-- Basic CTE
WITH active_users AS (
    SELECT id, name, email
    FROM users
    WHERE is_active = true
)
SELECT u.name, COUNT(o.id) AS order_count
FROM active_users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.name;
```

### Multiple CTEs

```sql
WITH
high_value_orders AS (
    SELECT user_id, SUM(total) AS total_spent
    FROM orders
    WHERE total > 100
    GROUP BY user_id
),
vip_users AS (
    SELECT u.id, u.name, h.total_spent
    FROM users u
    JOIN high_value_orders h ON u.id = h.user_id
    WHERE h.total_spent > 1000
)
SELECT * FROM vip_users ORDER BY total_spent DESC;
```

### CTE Materialization (PostgreSQL 12+)

By default, CTEs referenced **once** are inlined (optimized). CTEs referenced **multiple times** are materialized.

```sql
-- Force materialization (pre-12 behavior)
WITH active AS MATERIALIZED (
    SELECT * FROM users WHERE is_active = true
)
SELECT * FROM active;

-- Force inlining (allow optimizer to push filters down)
WITH active AS NOT MATERIALIZED (
    SELECT * FROM users WHERE is_active = true
)
SELECT * FROM active WHERE age > 25;
-- Without NOT MATERIALIZED, PostgreSQL might scan ALL active users first
```

---

## Recursive CTEs

For querying **hierarchical/tree data** and **graph traversal**.

```sql
-- Employee hierarchy (org chart)
WITH RECURSIVE org_chart AS (
    -- Base case: top-level managers (no manager)
    SELECT id, name, manager_id, 1 AS depth, ARRAY[name] AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: find subordinates
    SELECT e.id, e.name, e.manager_id, oc.depth + 1, oc.path || e.name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT
    repeat('  ', depth - 1) || name AS hierarchy,
    depth,
    array_to_string(path, ' → ') AS reporting_chain
FROM org_chart
ORDER BY path;
```

```
Output:
hierarchy           | depth | reporting_chain
--------------------|-------|-------------------------
CEO                 | 1     | CEO
  VP Engineering    | 2     | CEO → VP Engineering
    Lead Backend    | 3     | CEO → VP Engineering → Lead Backend
    Lead Frontend   | 3     | CEO → VP Engineering → Lead Frontend
  VP Marketing      | 2     | CEO → VP Marketing
```

### Generate Series

```sql
-- Generate a series of numbers
SELECT generate_series(1, 10);

-- Generate dates
SELECT generate_series(
    '2026-01-01'::date,
    '2026-12-31'::date,
    '1 month'::interval
) AS month;

-- Fill gaps in time-series data
SELECT
    d.day,
    COALESCE(o.daily_total, 0) AS revenue
FROM generate_series('2026-01-01'::date, '2026-01-31'::date, '1 day') d(day)
LEFT JOIN (
    SELECT date_trunc('day', created_at)::date AS day, SUM(total) AS daily_total
    FROM orders
    GROUP BY 1
) o ON d.day = o.day
ORDER BY d.day;
```

---

## Window Functions

Window functions compute values across a **set of rows related to the current row** without collapsing them into a single row (unlike GROUP BY).

### Syntax

```sql
function_name(args) OVER (
    [PARTITION BY column_list]
    [ORDER BY column_list]
    [frame_clause]
)
```

### ROW_NUMBER, RANK, DENSE_RANK

```sql
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num,
    RANK()       OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank
FROM employees;
```

```
name    | department  | salary | row_num | rank | dense_rank
--------|-------------|--------|---------|------|-----------
Alice   | Engineering | 150000 | 1       | 1    | 1
Bob     | Engineering | 140000 | 2       | 2    | 2
Charlie | Engineering | 140000 | 3       | 2    | 2    ← Same salary
Dave    | Engineering | 130000 | 4       | 4    | 3    ← rank skips 3, dense_rank doesn't
Eve     | Marketing   | 120000 | 1       | 1    | 1
```

**Differences:**
- `ROW_NUMBER()` — Always unique (arbitrary for ties)
- `RANK()` — Same rank for ties, **skips** numbers
- `DENSE_RANK()` — Same rank for ties, **no gaps**

### Aggregate Window Functions

```sql
SELECT
    name,
    department,
    salary,
    SUM(salary) OVER (PARTITION BY department) AS dept_total,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg,
    salary - AVG(salary) OVER (PARTITION BY department) AS diff_from_avg,
    round(100.0 * salary / SUM(salary) OVER (PARTITION BY department), 2) AS pct_of_dept
FROM employees;
```

### LAG and LEAD

Access **previous** or **next** rows without a self-join.

```sql
SELECT
    date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY date) AS prev_day_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) AS daily_change,
    LEAD(revenue, 1) OVER (ORDER BY date) AS next_day_revenue
FROM daily_sales;
```

### FIRST_VALUE, LAST_VALUE, NTH_VALUE

```sql
SELECT
    name,
    department,
    salary,
    FIRST_VALUE(name) OVER (PARTITION BY department ORDER BY salary DESC) AS highest_paid,
    LAST_VALUE(name)  OVER (
        PARTITION BY department ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS lowest_paid
FROM employees;
```

> **Gotcha:** `LAST_VALUE` default frame is `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, so you must specify `UNBOUNDED FOLLOWING` to get the actual last value!

### Running Totals and Moving Averages

```sql
SELECT
    date,
    revenue,
    -- Running total
    SUM(revenue) OVER (ORDER BY date) AS running_total,
    -- 7-day moving average
    AVG(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d,
    -- Cumulative percentage
    round(100.0 * SUM(revenue) OVER (ORDER BY date) /
          SUM(revenue) OVER (), 2) AS cumulative_pct
FROM daily_sales;
```

### Frame Clause

```
ROWS BETWEEN frame_start AND frame_end

frame_start / frame_end options:
  UNBOUNDED PRECEDING    ← From first row of partition
  N PRECEDING            ← N rows before current
  CURRENT ROW            ← Current row
  N FOLLOWING            ← N rows after current
  UNBOUNDED FOLLOWING    ← To last row of partition
```

```
Example: 3-row window centered on current row
ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING

Partition: [A] [B] [C] [D] [E]
For row C:      ← [B] [C] [D] →
```

### Named Windows

```sql
SELECT
    name, department, salary,
    ROW_NUMBER() OVER w AS row_num,
    RANK()       OVER w AS rank,
    SUM(salary)  OVER w AS running_total
FROM employees
WINDOW w AS (PARTITION BY department ORDER BY salary DESC);
```

---

## LATERAL Joins

`LATERAL` allows a subquery to **reference columns from preceding FROM items**. Think of it as a correlated subquery in the FROM clause.

```sql
-- Top 3 orders per user
SELECT u.name, t.order_id, t.total
FROM users u
CROSS JOIN LATERAL (
    SELECT o.id AS order_id, o.total
    FROM orders o
    WHERE o.user_id = u.id     -- References u.id from outer query!
    ORDER BY o.total DESC
    LIMIT 3
) t;

-- Without LATERAL, you'd need complex window functions:
-- ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC)
```

### LATERAL with Functions

```sql
-- Unnest arrays with LATERAL
SELECT p.title, t.tag
FROM posts p
CROSS JOIN LATERAL unnest(p.tags) AS t(tag);

-- JSON array expansion
SELECT o.id, item->>'name' AS item_name, (item->>'qty')::int AS qty
FROM orders o
CROSS JOIN LATERAL jsonb_array_elements(o.items) AS item;
```

---

## JSON / JSONB Operations (Advanced)

### Building JSON

```sql
-- Build JSON objects
SELECT json_build_object('name', name, 'email', email) FROM users;
-- {"name": "Alice", "email": "alice@test.com"}

-- Build JSON arrays
SELECT json_agg(name) FROM users;
-- ["Alice", "Bob", "Charlie"]

-- Build arrays of objects
SELECT json_agg(json_build_object('id', id, 'name', name)) FROM users;
-- [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

-- Row to JSON
SELECT row_to_json(u) FROM users u LIMIT 1;
-- {"id":1,"name":"Alice","email":"alice@test.com","age":30}

-- Aggregate into keyed object
SELECT jsonb_object_agg(name, salary) FROM employees;
-- {"Alice": 150000, "Bob": 140000}
```

### JSONB Path Queries (PostgreSQL 12+)

```sql
-- SQL/JSON path query
SELECT * FROM products
WHERE jsonb_path_exists(metadata, '$.tags[*] ? (@ == "sale")');

-- Extract values with path
SELECT jsonb_path_query(metadata, '$.tags[*]') FROM products;

-- Conditional path
SELECT jsonb_path_query_first(
    metadata,
    '$.variants[*] ? (@.price < 30)'
) FROM products;
```

### JSONB Indexing Strategies

```sql
-- GIN index on entire JSONB column (supports @>, ?, ?|, ?&)
CREATE INDEX idx_metadata ON products USING gin (metadata);

-- GIN index with jsonb_path_ops (smaller, supports @> only)
CREATE INDEX idx_metadata_path ON products USING gin (metadata jsonb_path_ops);

-- B-Tree index on specific JSONB field
CREATE INDEX idx_metadata_category ON products ((metadata->>'category'));
```

---

## Full-Text Search

PostgreSQL has **built-in full-text search** — no need for Elasticsearch for many use cases!

### Core Concepts

```sql
-- tsvector: document representation (sorted lexemes with positions)
SELECT to_tsvector('english', 'The quick brown foxes jumped over the lazy dogs');
-- 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- tsquery: search query
SELECT to_tsquery('english', 'quick & fox');
-- 'quick' & 'fox'

-- Match operator
SELECT to_tsvector('english', 'The quick brown fox') @@ to_tsquery('english', 'quick & fox');
-- true
```

### Practical Full-Text Search

```sql
-- Add a generated tsvector column
ALTER TABLE articles ADD COLUMN search_vector tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(body, '')), 'B')
) STORED;

-- Index it
CREATE INDEX idx_articles_search ON articles USING gin (search_vector);

-- Search with ranking
SELECT
    title,
    ts_rank(search_vector, query) AS rank,
    ts_headline('english', body, query, 'StartSel=<b>, StopSel=</b>, MaxWords=35') AS snippet
FROM articles,
     to_tsquery('english', 'postgres & (indexing | performance)') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;
```

### Search Operators

```sql
to_tsquery('english', 'cat & dog')       -- AND
to_tsquery('english', 'cat | dog')       -- OR
to_tsquery('english', '!cat')            -- NOT
to_tsquery('english', 'super <-> hero')  -- FOLLOWED BY (phrase search)
to_tsquery('english', 'cat <2> dog')     -- Within 2 words
```

---

## Useful SQL Patterns

### FILTER Clause

```sql
-- Instead of CASE WHEN inside aggregate
SELECT
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'active') AS active_count,
    COUNT(*) FILTER (WHERE status = 'inactive') AS inactive_count,
    AVG(age) FILTER (WHERE role = 'admin') AS admin_avg_age
FROM users;
```

### GROUPING SETS, CUBE, ROLLUP

```sql
-- Multiple grouping levels in one query
SELECT department, role, COUNT(*), SUM(salary)
FROM employees
GROUP BY GROUPING SETS (
    (department, role),   -- By department and role
    (department),         -- By department only
    ()                    -- Grand total
);

-- ROLLUP = hierarchical subtotals
SELECT department, role, COUNT(*)
FROM employees
GROUP BY ROLLUP (department, role);
-- Produces: (dept, role), (dept, NULL), (NULL, NULL)

-- CUBE = all possible combinations
SELECT department, role, COUNT(*)
FROM employees
GROUP BY CUBE (department, role);
-- Produces: (dept, role), (dept, NULL), (NULL, role), (NULL, NULL)
```

### DISTINCT ON

```sql
-- PostgreSQL-specific: first row per group
SELECT DISTINCT ON (user_id)
    user_id, created_at, status
FROM orders
ORDER BY user_id, created_at DESC;
-- Returns the LATEST order for each user
```

### INSERT ... ON CONFLICT (Upsert)

```sql
-- Upsert with detailed control
INSERT INTO products (sku, name, price, stock)
VALUES ('WIDGET-001', 'Widget', 29.99, 100)
ON CONFLICT (sku) DO UPDATE SET
    price = EXCLUDED.price,
    stock = products.stock + EXCLUDED.stock,  -- Add to existing stock
    updated_at = now()
WHERE products.price != EXCLUDED.price;       -- Only update if price changed
-- EXCLUDED refers to the row that failed to insert
```

### Returning with CTE (DML chains)

```sql
-- Delete old sessions AND insert them into archive in one statement
WITH deleted AS (
    DELETE FROM sessions
    WHERE expires_at < now() - interval '30 days'
    RETURNING *
)
INSERT INTO archived_sessions
SELECT * FROM deleted;
```

---

## Common Interview Questions — Advanced SQL

### Q1: Explain the difference between a CTE and a subquery.

| Feature | CTE | Subquery |
|---------|-----|----------|
| Readability | Named, self-documenting | Nested, harder to read |
| Reuse | Can be referenced multiple times | Must be duplicated |
| Recursion | Supports recursive queries | Cannot recurse |
| Optimization | Materialized or inlined (PG 12+) | Always inlined by optimizer |
| DML | Can contain INSERT/UPDATE/DELETE | Only in specific places |

**When to use CTE:** Complex multi-step queries, recursive hierarchies, DML chains with RETURNING.
**When to use subquery:** Simple filters, single-use, when optimizer needs to push filters down.

---

### Q2: How would you find the Nth highest salary?

```sql
-- Method 1: DENSE_RANK
SELECT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rank
    FROM employees
) ranked
WHERE rank = 3;

-- Method 2: DISTINCT + OFFSET
SELECT DISTINCT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 2;  -- 0-indexed, so OFFSET 2 = 3rd
```

---

### Q3: Find employees who earn more than their department average.

```sql
SELECT name, department, salary, dept_avg
FROM (
    SELECT
        name, department, salary,
        AVG(salary) OVER (PARTITION BY department) AS dept_avg
    FROM employees
) sub
WHERE salary > dept_avg;
```

---

### Q4: Find users who placed orders on 3 or more consecutive days.

```sql
WITH daily_orders AS (
    SELECT DISTINCT user_id, date_trunc('day', created_at)::date AS order_date
    FROM orders
),
grouped AS (
    SELECT
        user_id,
        order_date,
        order_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date))::int AS grp
    FROM daily_orders
),
consecutive AS (
    SELECT user_id, grp, COUNT(*) AS streak
    FROM grouped
    GROUP BY user_id, grp
    HAVING COUNT(*) >= 3
)
SELECT DISTINCT u.name, c.streak
FROM consecutive c
JOIN users u ON c.user_id = u.id;
```
