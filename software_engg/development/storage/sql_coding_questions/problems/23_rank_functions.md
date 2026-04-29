# Window Functions: RANK(), DENSE_RANK(), NTILE()

## Question 1: RANK() vs DENSE_RANK()
**Difficulty**: Medium

Given an `employees` table, rank employees by salary and show the difference between RANK() and DENSE_RANK().

### Table: employees
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| last_name | VARCHAR(50) |
| salary | DECIMAL(10,2) |

### Sample Data
```
employee_id | first_name | salary
1           | John       | 100
2           | Jane       | 100
3           | Bob        | 90
4           | Alice      | 80
5           | Charlie    | 80
6           | David      | 70
```

### Solution
```sql
SELECT first_name, salary,
       RANK() OVER (ORDER BY salary DESC) as rank_val,
       DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank_val
FROM employees;
```

### Output
```
first_name | salary | rank_val | dense_rank_val
John       | 100    | 1        | 1
Jane       | 100    | 1        | 1
Bob        | 90     | 3        | 2
Alice      | 80     | 4        | 3
Charlie    | 80     | 4        | 3
David      | 70     | 6        | 4
```

---

## Question 2: Find Nth Highest Salary
**Difficulty**: Medium

Find the 3rd highest salary using DENSE_RANK().

### Solution
```sql
SELECT DISTINCT salary
FROM (
    SELECT salary,
           DENSE_RANK() OVER (ORDER BY salary DESC) as rank_val
    FROM employees
) ranked
WHERE rank_val = 3;
```

---

## Question 3: NTILE() for Quartiles
**Difficulty**: Medium

Divide employees into 4 salary quartiles.

### Solution
```sql
SELECT first_name, salary,
       NTILE(4) OVER (ORDER BY salary) as quartile
FROM employees;
```

### Output
```
first_name | salary | quartile
David      | 70     | 1
Charlie    | 80     | 1
Alice      | 80     | 2
Bob        | 90     | 2
Jane       | 100    | 3
John       | 100    | 4
```

---

## Question 4: Rank Within Groups
**Difficulty**: Hard

Rank employees by salary within each department.

### Solution
```sql
SELECT first_name, department_id, salary,
       RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_rank,
       DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_dense_rank
FROM employees;
```

---

## Question 5: Top N Per Group
**Difficulty**: Hard

Find the top 2 highest paid employees in each department.

### Solution
```sql
SELECT * FROM (
    SELECT first_name, department_id, salary,
           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank_val
    FROM employees
) ranked
WHERE rank_val <= 2;
```

---

## Key Concepts

- **RANK()**: Assigns rank with gaps after ties (1,1,3,4)
- **DENSE_RANK()**: Assigns rank without gaps (1,1,2,3)
- **NTILE(n)**: Divides rows into n equal groups
- **PARTITION BY**: Resets ranking for each partition

## RANK() vs DENSE_RANK() vs ROW_NUMBER()

```
Salary:  100, 100, 90, 80, 80

ROW_NUMBER():    1, 2, 3, 4, 5  (unique numbers)
RANK():          1, 1, 3, 4, 4  (gaps after ties)
DENSE_RANK():    1, 1, 2, 3, 3  (no gaps)
```

## NTILE() Examples

```
NTILE(2) - Median split:  1, 1, 1, 2, 2, 2
NTILE(3) - Tertiles:      1, 1, 2, 2, 3, 3
NTILE(4) - Quartiles:     1, 1, 2, 2, 3, 3, 4, 4
```

## Common Interview Questions

1. Find the Nth highest salary
2. Find top 3 products per category
3. Divide customers into spending tiers
4. Rank scores with ties

## Practice Exercises

1. Find employees earning more than their department median
2. Rank products by sales within each category
3. Divide students into grade buckets (A, B, C, D, F)
4. Find the second highest salary in each department