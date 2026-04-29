# LEFT JOIN / RIGHT JOIN

## Question 1: Basic LEFT JOIN
**Difficulty**: Easy

Find all employees and their departments. Include employees who are not assigned to any department.

### Tables

**employees**
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| last_name | VARCHAR(50) |
| department_id | INT (FK) |

**departments**
| Column | Type |
|--------|------|
| department_id | INT (PK) |
| department_name | VARCHAR(100) |

### Sample Data
```
employees:
employee_id | first_name | department_id
1           | John       | 1
2           | Jane       | 2
3           | Bob        | NULL  (no department)

departments:
department_id | department_name
1             | IT
2             | HR
3             | Finance
```

### Solution
```sql
SELECT e.first_name, e.last_name, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id;
```

### Output
```
first_name | last_name | department_name
John       | Doe       | IT
Jane       | Smith     | HR
Bob        | Johnson   | NULL
```

---

## Question 2: RIGHT JOIN
**Difficulty**: Easy

Find all departments and their employees. Include departments with no employees.

### Solution
```sql
SELECT d.department_name, e.first_name, e.last_name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.department_id;
```

### Output
```
department_name | first_name | last_name
IT              | John       | Doe
HR              | Jane       | Smith
Finance         | NULL       | NULL
```

---

## Question 3: LEFT JOIN with NULL Check
**Difficulty**: Medium

Find employees who are NOT assigned to any department.

### Solution
```sql
SELECT e.first_name, e.last_name, e.department_id
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
WHERE d.department_id IS NULL;
```

---

## Question 4: Find Missing Records
**Difficulty**: Medium

Find departments that have no employees.

### Solution
```sql
SELECT d.department_name
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
WHERE e.employee_id IS NULL;
```

---

## Question 5: LEFT JOIN with Aggregation
**Difficulty**: Hard

Find the number of employees in each department, including departments with 0 employees.

### Solution
```sql
SELECT d.department_name, COUNT(e.employee_id) as employee_count
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name
ORDER BY employee_count DESC;
```

---

## Question 6: Multiple LEFT JOINs
**Difficulty**: Hard

Find all customers and their orders, including customers with no orders. Also show order totals.

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
| total_amount | DECIMAL(10,2) |

### Solution
```sql
SELECT c.customer_name, o.order_id, o.total_amount,
       COALESCE(o.total_amount, 0) as amount_or_zero
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_name, o.order_id;
```

---

## Key Concepts

- **LEFT JOIN**: Returns all rows from left table, matching rows from right table
- **RIGHT JOIN**: Returns all rows from right table, matching rows from left table
- **NULL handling**: Non-matching rows get NULL values
- **WHERE vs ON**: Filter in WHERE excludes NULLs, filter in ON doesn't

## LEFT JOIN Visual

```
Table A          Table B
1                3
2                4
3                5
4
5

LEFT JOIN on A.id = B.id:
Result: All A rows (1,2,3,4,5) with B where match, NULL otherwise
```

## LEFT JOIN vs INNER JOIN

```sql
-- INNER JOIN: Only matching rows
SELECT * FROM A INNER JOIN B ON A.id = B.id;
-- Result: 3, 4, 5

-- LEFT JOIN: All A rows
SELECT * FROM A LEFT JOIN B ON A.id = B.id;
-- Result: 1(NULL), 2(NULL), 3(3), 4(4), 5(5)
```

## Common Interview Questions

1. Find customers who never placed an order
2. Find departments with no employees
3. List all products with their sales (including unsold)
4. Find employees without managers

## Practice Exercises

1. Find all users and their last login date (including users who never logged in)
2. List all courses and enrolled students (including empty courses)
3. Find products that have never been ordered
4. Calculate total sales per customer (including customers with no orders)