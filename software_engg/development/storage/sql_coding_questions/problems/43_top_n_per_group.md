# Top N Per Group

## Question 1: Top 3 Salaries Per Department
**Difficulty**: Medium

Find the top 3 highest paid employees in each department.

### Table: employees
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| department_id | INT |
| salary | DECIMAL(10,2) |

### Sample Data
```
employee_id | first_name | department_id | salary
1           | John       | 1             | 50000
2           | Jane       | 1             | 60000
3           | Bob        | 1             | 55000
4           | Alice      | 2             | 65000
5           | Charlie    | 2             | 70000
6           | David      | 2             | 45000
```

### Solution using ROW_NUMBER()
```sql
SELECT first_name, department_id, salary
FROM (
    SELECT first_name, department_id, salary,
           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as rn
    FROM employees
) ranked
WHERE rn <= 3;
```

### Solution using DENSE_RANK() (handles ties)
```sql
SELECT first_name, department_id, salary
FROM (
    SELECT first_name, department_id, salary,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dr
    FROM employees
) ranked
WHERE dr <= 3;
```

---

## Question 2: Latest Order Per Customer
**Difficulty**: Medium

Find the most recent order for each customer.

### Tables

**customers**
| Column | Type |
|--------|------|
| customer_id | INT (PK) |
| customer_name | VARCHAR(100) |

**orders**
| Column | Type |
|--------|------|
| order_id | INT (PK) |
| customer_id | INT |
| order_date | DATE |
| amount | DECIMAL(10,2) |

### Solution
```sql
SELECT customer_name, order_id, order_date, amount
FROM (
    SELECT c.customer_name, o.order_id, o.order_date, o.amount,
           ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC) as rn
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
) ranked
WHERE rn = 1;
```

---

## Question 3: Second Highest Salary Per Department
**Difficulty**: Hard

Find the second highest salary in each department.

### Solution
```sql
SELECT first_name, department_id, salary
FROM (
    SELECT first_name, department_id, salary,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dr
    FROM employees
) ranked
WHERE dr = 2;
```

---

## Question 4: Top N with Ties
**Difficulty**: Hard

Find all employees who earn the top 3 salaries (include ties).

### Solution using DENSE_RANK()
```sql
SELECT first_name, department_id, salary
FROM (
    SELECT first_name, department_id, salary,
           DENSE_RANK() OVER (ORDER BY salary DESC) as dr
    FROM employees
) ranked
WHERE dr <= 3;
```

---

## Question 5: First Purchase Per Customer
**Difficulty**: Medium

Find each customer's first purchase.

### Solution
```sql
SELECT customer_id, order_id, order_date, amount
FROM (
    SELECT customer_id, order_id, order_date, amount,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date ASC) as rn
    FROM orders
) ranked
WHERE rn = 1;
```

---

## Key Concepts

- **ROW_NUMBER()**: Unique rank per row (1,2,3)
- **DENSE_RANK()**: Rank with ties (1,1,2,3)
- **PARTITION BY**: Reset ranking for each group
- **Subquery required**: Window functions can't be in WHERE clause

## Common Patterns

```sql
-- Top N per group
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY group_col ORDER BY value DESC) as rn
    FROM table
) WHERE rn <= N;

-- Nth value per group
SELECT * FROM (
    SELECT *, DENSE_RANK() OVER (PARTITION BY group_col ORDER BY value DESC) as dr
    FROM table
) WHERE dr = N;
```

## ROW_NUMBER() vs DENSE_RANK() vs RANK()

| Function | Ties | Gaps | Use Case |
|----------|------|------|----------|
| ROW_NUMBER() | Different ranks | No | Exactly N rows |
| DENSE_RANK() | Same rank | No | All ties included |
| RANK() | Same rank | Yes | Skip after ties |

## Common Interview Questions

1. Find top 3 products per category
2. Find latest record per user
3. Find Nth highest salary per department
4. Find first and last purchase per customer

## Practice Exercises

1. Find the most recent login per user
2. Find top 5 customers by spending per month
3. Find the second order per customer
4. Find highest paid employee per department