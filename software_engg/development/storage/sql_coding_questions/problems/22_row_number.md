# Window Functions: ROW_NUMBER()

## Question 1: Basic ROW_NUMBER()
**Difficulty**: Medium

Given an `employees` table, assign a unique row number to each employee based on salary (highest salary = 1).

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
employee_id | first_name | last_name | department_id | salary
1           | John       | Doe       | 1             | 50000
2           | Jane       | Smith     | 2             | 60000
3           | Bob        | Johnson   | 1             | 55000
4           | Alice      | Brown     | 2             | 65000
5           | Charlie    | Davis     | 1             | 45000
```

### Solution
```sql
SELECT first_name, last_name, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC) as salary_rank
FROM employees;
```

### Output
```
first_name | last_name | salary | salary_rank
Alice      | Brown     | 65000  | 1
Jane       | Smith     | 60000  | 2
Bob        | Johnson   | 55000  | 3
John       | Doe       | 50000  | 4
Charlie    | Davis     | 45000  | 5
```

---

## Question 2: ROW_NUMBER() with PARTITION BY
**Difficulty**: Medium

Find the row number of each employee within their department, ordered by salary.

### Solution
```sql
SELECT first_name, last_name, department_id, salary,
       ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_salary_rank
FROM employees;
```

### Output
```
first_name | last_name | department_id | salary | dept_salary_rank
John       | Doe       | 1             | 50000  | 2
Bob        | Johnson   | 1             | 55000  | 1
Charlie    | Davis     | 1             | 45000  | 3
Alice      | Brown     | 2             | 65000  | 1
Jane       | Smith     | 2             | 60000  | 2
```

---

## Question 3: Top N Per Group
**Difficulty**: Hard

Find the top 3 highest paid employees in each department.

### Solution
```sql
SELECT * FROM (
    SELECT first_name, last_name, department_id, salary,
           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as rn
    FROM employees
) ranked
WHERE rn <= 3;
```

---

## Question 4: Remove Duplicates
**Difficulty**: Medium

Given a table with duplicate records, delete all duplicates keeping only one.

### Table: duplicates
| Column | Type |
|--------|------|
| id | INT |
| email | VARCHAR(100) |
| name | VARCHAR(50) |

### Sample Data
```
id | email           | name
1  | john@test.com   | John
2  | john@test.com   | John
3  | jane@test.com   | Jane
4  | jane@test.com   | Jane
5  | jane@test.com   | Jane
```

### Solution
```sql
DELETE FROM duplicates
WHERE id IN (
    SELECT id FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) as rn
        FROM duplicates
    ) dup
    WHERE rn > 1
);
```

---

## Question 5: Pagination
**Difficulty**: Medium

Implement pagination to get employees 11-20 when sorted by salary.

### Solution
```sql
SELECT * FROM (
    SELECT employee_id, first_name, last_name, salary,
           ROW_NUMBER() OVER (ORDER BY salary DESC) as rn
    FROM employees
) ranked
WHERE rn BETWEEN 11 AND 20;
```

---

## Key Concepts

- **ROW_NUMBER()**: Assigns unique sequential integers to rows
- **OVER clause**: Defines the window for the function
- **ORDER BY in OVER**: Determines the ordering for row numbering
- **PARTITION BY**: Resets row numbers for each partition

## ROW_NUMBER() vs RANK() vs DENSE_RANK()

```
Salary:  100, 100, 90, 80

ROW_NUMBER():    1, 2, 3, 4  (unique numbers)
RANK():          1, 1, 3, 4  (gaps after ties)
DENSE_RANK():    1, 1, 2, 3  (no gaps)
```

## Common Interview Questions

1. Find the Nth highest salary
2. Find top N records per group
3. Remove duplicate rows
4. Implement pagination
5. Find consecutive numbers

## Practice Exercises

1. Find the 3rd highest salary in each department
2. Rank customers by total order amount
3. Find duplicate emails in a user table
4. Get every other row from a table