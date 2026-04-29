# Correlated Subqueries

## Question 1: Basic Correlated Subquery
**Difficulty**: Medium

Find all employees who earn more than the average salary in their department.

### Table: employees
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| last_name | VARCHAR(50) |
| department_id | INT |
| salary | DECIMAL(10,2) |

### Sample Data
```
employee_id | first_name | department_id | salary
1           | John       | 1             | 50000
2           | Jane       | 1             | 60000
3           | Bob        | 2             | 55000
4           | Alice      | 2             | 45000
```

### Solution
```sql
SELECT first_name, salary, department_id
FROM employees e
WHERE salary > (
    SELECT AVG(salary)
    FROM employees
    WHERE department_id = e.department_id
);
```

### Output
```
first_name | salary | department_id
Jane       | 60000  | 1
Bob        | 55000  | 2
```

---

## Question 2: EXISTS Correlated Subquery
**Difficulty**: Medium

Find customers who have placed at least one order.

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

### Solution
```sql
SELECT customer_name
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

---

## Question 3: NOT EXISTS
**Difficulty**: Medium

Find customers who have NOT placed any orders.

### Solution
```sql
SELECT customer_name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
);
```

---

## Question 4: Correlated Subquery in SELECT
**Difficulty**: Hard

List all employees with their salary and department average.

### Solution
```sql
SELECT first_name, salary, department_id,
       (SELECT AVG(salary)
        FROM employees
        WHERE department_id = e.department_id) as dept_avg
FROM employees e;
```

---

## Question 5: Find Nth Highest Salary
**Difficulty**: Hard

Find the 3rd highest salary using correlated subquery.

### Solution
```sql
SELECT DISTINCT salary
FROM employees e1
WHERE 3 = (
    SELECT COUNT(DISTINCT salary)
    FROM employees e2
    WHERE e2.salary >= e1.salary
);
```

---

## Key Concepts

- **Correlated subquery**: Inner query references outer query
- **Executes per row**: Runs once for each row in outer query
- **Performance**: Can be slow on large datasets
- **EXISTS/NOT EXISTS**: Common correlated patterns

## Correlated vs Non-Correlated

```sql
-- Non-correlated (runs once)
SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- Correlated (runs per row)
SELECT * FROM employees e
WHERE salary > (
    SELECT AVG(salary) FROM employees
    WHERE department_id = e.department_id
);
```

## Common Interview Questions

1. Find employees earning more than department average
2. Find customers with no orders
3. Find products not sold in last month
4. Find duplicate emails

## Practice Exercises

1. Find departments with above-average salary
2. Find employees with salary above company average
3. Find customers who ordered all products
4. Find the second highest salary per department