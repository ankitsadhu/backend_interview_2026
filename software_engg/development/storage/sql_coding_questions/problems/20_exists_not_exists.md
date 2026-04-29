# EXISTS and NOT EXISTS

## Question 1: Basic EXISTS
**Difficulty**: Medium

Find all customers who have placed at least one order.

### Tables

**customers**
| Column | Type |
|--------|------|
| customer_id | INT (PK) |
| customer_name | VARCHAR(100) |
| email | VARCHAR(100) |

**orders**
| Column | Type |
|--------|------|
| order_id | INT (PK) |
| customer_id | INT |
| order_date | DATE |
| amount | DECIMAL(10,2) |

### Sample Data
```
customers:
customer_id | customer_name | email
1           | Alice         | alice@test.com
2           | Bob           | bob@test.com
3           | Charlie       | charlie@test.com

orders:
order_id | customer_id | order_date  | amount
1        | 1           | 2024-01-01  | 100
2        | 1           | 2024-01-15  | 200
3        | 3           | 2024-02-01  | 150
```

### Solution
```sql
SELECT customer_name, email
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

### Output
```
customer_name | email
Alice         | alice@test.com
Charlie       | charlie@test.com
```

---

## Question 2: NOT EXISTS
**Difficulty**: Medium

Find all customers who have NOT placed any orders.

### Solution
```sql
SELECT customer_name, email
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

### Output
```
customer_name | email
Bob           | bob@test.com
```

---

## Question 3: EXISTS with Condition
**Difficulty**: Hard

Find customers who have placed an order worth more than $500.

### Solution
```sql
SELECT customer_name, email
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
      AND o.amount > 500
);
```

---

## Question 4: Double NOT EXISTS (Division)
**Difficulty**: Hard

Find customers who have ordered ALL products.

### Tables

**products**
| Column | Type |
|--------|------|
| product_id | INT (PK) |
| product_name | VARCHAR(100) |

**order_items**
| Column | Type |
|--------|------|
| order_id | INT |
| product_id | INT |

### Solution
```sql
SELECT customer_name
FROM customers c
WHERE NOT EXISTS (
    SELECT product_id
    FROM products p
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.customer_id = c.customer_id
          AND oi.product_id = p.product_id
    )
);
```

---

## Question 5: EXISTS vs IN
**Difficulty**: Medium

Compare EXISTS and IN approaches for finding customers with orders.

### Using EXISTS (Better for large order table)
```sql
SELECT customer_name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

### Using IN (Better for small order table)
```sql
SELECT customer_name
FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders
);
```

---

## Key Concepts

- **EXISTS**: Returns true if subquery returns any rows
- **NOT EXISTS**: Returns true if subquery returns no rows
- **Correlated**: EXISTS subqueries are usually correlated
- **Performance**: EXISTS stops at first match, IN evaluates all

## EXISTS vs IN

| Feature | EXISTS | IN |
|---------|--------|-----|
| NULL handling | Handles NULLs | May fail with NULLs |
| Performance | Better for large tables | Better for small tables |
| Early termination | Yes (stops at first match) | No (evaluates all) |

## Common Interview Questions

1. Find employees with no subordinates
2. Find products never ordered
3. Find customers who ordered all products
4. Find departments with no employees

## Practice Exercises

1. Find authors who have published books
2. Find students who haven't submitted assignments
3. Find cities with no customers
4. Find products available but never sold