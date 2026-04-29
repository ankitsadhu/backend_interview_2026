# HAVING Clause

## Question 1: Basic HAVING
**Difficulty**: Easy

Find departments with more than 5 employees.

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
5           | Charlie    | 1             | 52000
6           | David      | 1             | 48000
7           | Eve        | 1             | 51000
```

### Solution
```sql
SELECT department_id, COUNT(*) as employee_count
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5;
```

### Output
```
department_id | employee_count
1             | 5
```

---

## Question 2: HAVING with SUM
**Difficulty**: Medium

Find departments where total salary is greater than $200,000.

### Solution
```sql
SELECT department_id, SUM(salary) as total_salary
FROM employees
GROUP BY department_id
HAVING SUM(salary) > 200000;
```

---

## Question 3: HAVING with AVG
**Difficulty**: Medium

Find departments with average salary greater than $50,000.

### Solution
```sql
SELECT department_id, AVG(salary) as avg_salary
FROM employees
GROUP BY department_id
HAVING AVG(salary) > 50000;
```

---

## Question 4: WHERE vs HAVING
**Difficulty**: Medium

Find departments with more than 3 employees where average salary is above $45,000.

### Solution
```sql
SELECT department_id, 
       COUNT(*) as employee_count,
       AVG(salary) as avg_salary
FROM employees
WHERE salary > 30000  -- Filter individual rows BEFORE grouping
GROUP BY department_id
HAVING COUNT(*) > 3   -- Filter groups AFTER grouping
   AND AVG(salary) > 45000;
```

---

## Question 5: HAVING with Multiple Conditions
**Difficulty**: Hard

Find departments with at least 2 employees and total salary between $100,000 and $300,000.

### Solution
```sql
SELECT department_id, 
       COUNT(*) as employee_count,
       SUM(salary) as total_salary
FROM employees
GROUP BY department_id
HAVING COUNT(*) >= 2 
   AND SUM(salary) BETWEEN 100000 AND 300000;
```

---

## Key Concepts

- **HAVING**: Filters groups AFTER aggregation
- **WHERE**: Filters rows BEFORE aggregation
- **Aggregate in HAVING**: Can use COUNT, SUM, AVG, etc.
- **Order**: WHERE → GROUP BY → HAVING

## WHERE vs HAVING

| Clause | When Applied | Can Use Aggregates? |
|--------|--------------|---------------------|
| WHERE  | Before GROUP BY | No |
| HAVING | After GROUP BY | Yes |

## Query Execution Order
```sql
SELECT department_id, COUNT(*)
FROM employees
WHERE salary > 30000      -- 1. Filter rows
GROUP BY department_id    -- 2. Group rows
HAVING COUNT(*) > 5       -- 3. Filter groups
ORDER BY COUNT(*) DESC;   -- 4. Sort results
```

## Common Interview Questions

1. Find customers with more than 10 orders
2. Find products with total sales above $10,000
3. Find departments with average salary above company average
4. Find dates with more than 100 transactions

## Practice Exercises

1. Find products ordered more than 5 times
2. Find customers with total spending above $1000
3. Find months with more than 20 orders
4. Find categories with average price above $50