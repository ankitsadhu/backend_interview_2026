# CTE (Common Table Expressions) - WITH Clause

## Question 1: Basic CTE
**Difficulty**: Medium

Rewrite the following query using a CTE to find employees with salary above the average.

### Table: employees
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| last_name | VARCHAR(50) |
| department_id | INT |
| salary | DECIMAL(10,2) |

### Solution
```sql
WITH avg_salary AS (
    SELECT AVG(salary) as avg_sal
    FROM employees
)
SELECT e.first_name, e.last_name, e.salary
FROM employees e
CROSS JOIN avg_salary
WHERE e.salary > avg_salary.avg_sal;
```

---

## Question 2: Multiple CTEs
**Difficulty**: Medium

Find departments with above-average salary and list their employees.

### Solution
```sql
WITH dept_avg AS (
    SELECT department_id, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department_id
),
high_paying_depts AS (
    SELECT department_id
    FROM dept_avg
    WHERE avg_salary > 50000
)
SELECT e.first_name, e.last_name, e.salary, d.department_id
FROM employees e
JOIN high_paying_depts d ON e.department_id = d.department_id
ORDER BY e.salary DESC;
```

---

## Question 3: CTE for Readability
**Difficulty**: Medium

Find the second highest salary using CTE.

### Solution
```sql
WITH ranked_salaries AS (
    SELECT salary,
           DENSE_RANK() OVER (ORDER BY salary DESC) as rank
    FROM employees
)
SELECT DISTINCT salary
FROM ranked_salaries
WHERE rank = 2;
```

---

## Question 4: CTE vs Subquery
**Difficulty**: Medium

Compare CTE and subquery approaches for finding employees earning more than their department average.

### CTE Approach (Cleaner)
```sql
WITH dept_avg AS (
    SELECT department_id, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT e.first_name, e.last_name, e.salary, e.department_id, d.avg_salary
FROM employees e
JOIN dept_avg d ON e.department_id = d.department_id
WHERE e.salary > d.avg_salary;
```

### Subquery Approach (Harder to read)
```sql
SELECT e.first_name, e.last_name, e.salary, e.department_id,
       (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id) as avg_salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(salary) 
    FROM employees 
    WHERE department_id = e.department_id
);
```

---

## Question 5: Chained CTEs
**Difficulty**: Hard

Find departments where the maximum salary is more than twice the minimum salary.

### Solution
```sql
WITH dept_stats AS (
    SELECT department_id, 
           MIN(salary) as min_salary,
           MAX(salary) as max_salary
    FROM employees
    GROUP BY department_id
),
high_variance_depts AS (
    SELECT department_id
    FROM dept_stats
    WHERE max_salary > 2 * min_salary
)
SELECT d.department_name, ds.min_salary, ds.max_salary
FROM high_variance_depts ds
JOIN departments d ON ds.department_id = d.department_id;
```

---

## Key Concepts

- **WITH clause**: Defines a temporary named result set
- **CTE scope**: Only exists for the duration of the query
- **Multiple CTEs**: Separate with commas
- **Readability**: CTEs make complex queries easier to understand

## CTE Syntax
```sql
WITH cte_name AS (
    SELECT ...
),
cte_name2 AS (
    SELECT ... FROM cte_name
)
SELECT ... FROM cte_name2;
```

## CTE vs Temp Table vs Subquery

| Feature | CTE | Temp Table | Subquery |
|---------|-----|------------|----------|
| Scope | Single query | Session | Single query |
| Reusable | Yes (in query) | Yes | No |
| Performance | Similar | Can be indexed | Varies |
| Readability | High | Medium | Low |

## Common Interview Questions

1. Find Nth highest salary using CTE
2. Calculate running totals with CTE
3. Find duplicates using CTE
4. Compare performance of CTE vs subquery

## Practice Exercises

1. Find employees earning more than their department average
2. List departments with more than 10 employees
3. Find the department with the highest average salary
4. Calculate the salary difference from department average