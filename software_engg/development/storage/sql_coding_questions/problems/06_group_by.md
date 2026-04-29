# GROUP BY

## Question 1: Basic GROUP BY
**Difficulty**: Easy

Find the total salary for each department.

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
3           | Bob        | 2             | 55000
4           | Alice      | 2             | 45000
```

### Solution
```sql
SELECT department_id, SUM(salary) as total_salary
FROM employees
GROUP BY department_id;
```

### Output
```
department_id | total_salary
1             | 110000
2             | 100000
```

---

## Question 2: COUNT with GROUP BY
**Difficulty**: Easy

Find the number of employees in each department.

### Solution
```sql
SELECT department_id, COUNT(*) as employee_count
FROM employees
GROUP BY department_id;
```

---

## Question 3: Multiple Aggregations
**Difficulty**: Medium

Find the count, average, min, and max salary per department.

### Solution
```sql
SELECT department_id, 
       COUNT(*) as employee_count,
       AVG(salary) as avg_salary,
       MIN(salary) as min_salary,
       MAX(salary) as max_salary,
       SUM(salary) as total_salary
FROM employees
GROUP BY department_id;
```

---

## Question 4: GROUP BY with Multiple Columns
**Difficulty**: Medium

Find the number of employees and total salary for each department and job title.

### Solution
```sql
SELECT department_id, job_title, 
       COUNT(*) as employee_count,
       AVG(salary) as avg_salary
FROM employees
GROUP BY department_id, job_title
ORDER BY department_id, avg_salary DESC;
```

---

## Question 5: GROUP BY with Expressions
**Difficulty**: Hard

Find the number of employees hired per year.

### Solution
```sql
SELECT EXTRACT(YEAR FROM hire_date) as hire_year,
       COUNT(*) as employees_hired
FROM employees
GROUP BY EXTRACT(YEAR FROM hire_date)
ORDER BY hire_year;
```

---

## Key Concepts

- **GROUP BY**: Groups rows with same values
- **Aggregate functions**: COUNT, SUM, AVG, MIN, MAX
- **Non-aggregated columns**: Must be in GROUP BY clause
- **NULL handling**: NULLs are grouped together

## GROUP BY Execution Order
```
1. FROM - Get data
2. WHERE - Filter rows
3. GROUP BY - Group rows
4. HAVING - Filter groups
5. SELECT - Choose columns
6. ORDER BY - Sort results
```

## Common Interview Questions

1. Count orders per customer
2. Average salary per department
3. Total sales per product category
4. Number of users per signup month

## Practice Exercises

1. Find average salary per department
2. Count products per category
3. Find total sales per customer
4. Count orders per month