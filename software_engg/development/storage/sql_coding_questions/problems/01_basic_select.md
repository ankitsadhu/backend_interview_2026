# Basic SELECT, WHERE, ORDER BY

## Question 1: Select Specific Columns
**Difficulty**: Easy

Given an `employees` table, write a query to retrieve the first name, last name, and salary of all employees.

### Table: employees
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| last_name | VARCHAR(50) |
| email | VARCHAR(100) |
| department_id | INT |
| salary | DECIMAL(10,2) |
| hire_date | DATE |

### Solution
```sql
SELECT first_name, last_name, salary
FROM employees;
```

---

## Question 2: Filter with WHERE
**Difficulty**: Easy

Find all employees who earn more than $50,000.

### Solution
```sql
SELECT first_name, last_name, salary
FROM employees
WHERE salary > 50000;
```

---

## Question 3: ORDER BY
**Difficulty**: Easy

List all employees sorted by salary in descending order.

### Solution
```sql
SELECT first_name, last_name, salary
FROM employees
ORDER BY salary DESC;
```

---

## Question 4: Multiple Conditions
**Difficulty**: Easy

Find employees in department 5 who earn more than $60,000.

### Solution
```sql
SELECT first_name, last_name, department_id, salary
FROM employees
WHERE department_id = 5 AND salary > 60000;
```

---

## Question 5: OR Condition
**Difficulty**: Easy

Find employees in department 3 OR department 5.

### Solution
```sql
SELECT first_name, last_name, department_id
FROM employees
WHERE department_id = 3 OR department_id = 5;
```

---

## Key Concepts

- **SELECT**: Specifies columns to retrieve
- **FROM**: Specifies the table
- **WHERE**: Filters rows based on conditions
- **ORDER BY**: Sorts results (ASC or DESC)
- **AND/OR**: Combine multiple conditions

## Common Interview Questions

1. Find employees with salary between 30000 and 70000
2. List employees hired after a specific date
3. Find employees whose name starts with 'J'
4. Get top 5 highest paid employees

## Practice Exercises

1. Find all employees with salary greater than 50000, sorted by salary descending
2. List employee names and hire dates for department 10
3. Find employees hired in 2023