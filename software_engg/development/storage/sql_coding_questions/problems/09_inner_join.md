# INNER JOIN

## Question 1: Basic INNER JOIN
**Difficulty**: Easy

Given `employees` and `departments` tables, write a query to display employee names along with their department names.

### Tables

**employees**
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| last_name | VARCHAR(50) |
| department_id | INT |
| salary | DECIMAL(10,2) |

**departments**
| Column | Type |
|--------|------|
| department_id | INT (PK) |
| department_name | VARCHAR(100) |
| location | VARCHAR(100) |

### Sample Data
```
employees:
employee_id | first_name | last_name | department_id | salary
1           | John       | Doe       | 1             | 50000
2           | Jane       | Smith     | 2             | 60000
3           | Bob        | Johnson   | 1             | 55000

departments:
department_id | department_name | location
1             | IT              | New York
2             | HR              | Chicago
3             | Finance         | LA
```

### Solution
```sql
SELECT e.first_name, e.last_name, d.department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id;
```

### Output
```
first_name | last_name | department_name
John       | Doe       | IT
Jane       | Smith     | HR
Bob        | Johnson   | IT
```

---

## Question 2: JOIN with WHERE
**Difficulty**: Medium

Find all employees in the 'IT' department with salary greater than $50,000.

### Solution
```sql
SELECT e.first_name, e.last_name, e.salary, d.department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'IT' AND e.salary > 50000;
```

---

## Question 3: JOIN with Aggregation
**Difficulty**: Medium

Find the total salary expense for each department.

### Solution
```sql
SELECT d.department_name, SUM(e.salary) as total_salary
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name
ORDER BY total_salary DESC;
```

---

## Question 4: Multiple JOINs
**Difficulty**: Medium

Given `orders`, `customers`, and `products` tables, find all orders with customer names and product names.

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
| product_id | INT |
| quantity | INT |

**products**
| Column | Type |
|--------|------|
| product_id | INT (PK) |
| product_name | VARCHAR(100) |
| price | DECIMAL(10,2) |

### Solution
```sql
SELECT c.customer_name, p.product_name, o.quantity, 
       (o.quantity * p.price) as total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p ON o.product_id = p.product_id;
```

---

## Question 5: Self JOIN
**Difficulty**: Hard

Find all employees and their managers (manager_id references employee_id).

### Solution
```sql
SELECT e.first_name as employee, e.last_name as emp_last,
       m.first_name as manager, m.last_name as mgr_last
FROM employees e
INNER JOIN employees m ON e.manager_id = m.employee_id;
```

---

## Key Concepts

- **INNER JOIN**: Returns only matching rows from both tables
- **ON clause**: Specifies the join condition
- **Table aliases**: Use short aliases (e, d) for readability
- **Multiple JOINs**: Chain JOINs for complex queries

## INNER JOIN Visual

```
Table A          Table B
1                3
2                4
3                5
4
5

INNER JOIN on A.id = B.id:
Result: 3, 4, 5 (only matching values)
```

## Common Interview Questions

1. Find employees and their departments
2. Find orders with customer and product details
3. Find employees with their managers
4. Calculate total sales per category

## Practice Exercises

1. Find all employees who work in 'Sales' department
2. List department names with more than 5 employees
3. Find the highest paid employee in each department