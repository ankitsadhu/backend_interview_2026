# SELF JOIN

## Question 1: Employee-Manager Hierarchy
**Difficulty**: Medium

Given an `employees` table where `manager_id` references `employee_id`, find all employees and their managers.

### Table: employees
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| last_name | VARCHAR(50) |
| manager_id | INT (FK to employee_id) |

### Sample Data
```
employee_id | first_name | manager_id
1           | Alice      | NULL  (CEO)
2           | Bob        | 1
3           | Charlie    | 1
4           | David      | 2
5           | Eve        | 2
6           | Frank      | 3
```

### Solution
```sql
SELECT e.first_name as employee, 
       m.first_name as manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
ORDER BY e.employee_id;
```

### Output
```
employee | manager
Alice    | NULL
Bob      | Alice
Charlie  | Alice
David    | Bob
Eve      | Bob
Frank    | Charlie
```

---

## Question 2: Find Employees in Same Department
**Difficulty**: Medium

Find all pairs of employees who work in the same department.

### Solution
```sql
SELECT e1.first_name as employee1, 
       e2.first_name as employee2,
       e1.department_id
FROM employees e1
JOIN employees e2 ON e1.department_id = e2.department_id
WHERE e1.employee_id < e2.employee_id;
```

---

## Question 3: Compare with Previous Record
**Difficulty**: Hard

Find employees who earn more than their manager.

### Solution
```sql
SELECT e.first_name as employee, 
       e.salary as emp_salary,
       m.first_name as manager,
       m.salary as mgr_salary
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id
WHERE e.salary > m.salary;
```

---

## Question 4: Find Orphan Records
**Difficulty**: Medium

Find all employees who don't have a manager (excluding the CEO).

### Solution
```sql
SELECT e.first_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
WHERE e.manager_id IS NOT NULL AND m.employee_id IS NULL;
```

---

## Question 5: Hierarchical Query (3 Levels)
**Difficulty**: Hard

Find all employees, their managers, and their manager's managers (3 levels).

### Solution
```sql
SELECT e.first_name as employee,
       m.first_name as manager,
       gm.first_name as grand_manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
LEFT JOIN employees gm ON m.manager_id = gm.employee_id;
```

---

## Key Concepts

- **SELF JOIN**: Join a table to itself
- **Table aliases**: Essential for self joins (e1, e2 or e, m)
- **Hierarchical data**: Employee-manager, category-parent relationships
- **Avoid duplicates**: Use conditions like `e1.id < e2.id` for pairs

## SELF JOIN Patterns

```
1. Parent-Child: Find children and their parents
2. Comparison: Compare rows within same table
3. Hierarchy: Multiple levels of relationships
4. Pairs: Find all pairs meeting a condition
```

## Common Interview Questions

1. Find employees earning more than their manager
2. Find all pairs of friends (mutual relationship)
3. Find products sold together in same order
4. Find consecutive numbers in a sequence

## Practice Exercises

1. Find all employees who share the same hire date
2. List all categories and their parent categories
3. Find customers who live in the same city
4. Find products with the same price