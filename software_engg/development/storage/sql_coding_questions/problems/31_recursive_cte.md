# Recursive CTE (Hierarchies & Sequences)

## Question 1: Employee Hierarchy
**Difficulty**: Hard

Given an `employees` table with `manager_id`, find all employees under a specific manager (recursive hierarchy).

### Table: employees
| Column | Type |
|--------|------|
| employee_id | INT (PK) |
| first_name | VARCHAR(50) |
| manager_id | INT (FK) |

### Sample Data
```
employee_id | first_name | manager_id
1           | Alice      | NULL  (CEO)
2           | Bob        | 1
3           | Charlie    | 1
4           | David      | 2
5           | Eve        | 2
6           | Frank      | 3
7           | Grace      | 4
```

### Solution - Find all employees under Alice (employee_id = 1)
```sql
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor: Start with the manager
    SELECT employee_id, first_name, manager_id, 0 as level
    FROM employees
    WHERE employee_id = 1
    
    UNION ALL
    
    -- Recursive: Find all direct reports
    SELECT e.employee_id, e.first_name, e.manager_id, eh.level + 1
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT * FROM employee_hierarchy;
```

### Output
```
employee_id | first_name | manager_id | level
1           | Alice      | NULL       | 0
2           | Bob        | 1          | 1
3           | Charlie    | 1          | 1
4           | David      | 2          | 2
5           | Eve        | 2          | 2
6           | Frank      | 3          | 2
7           | Grace      | 4          | 3
```

---

## Question 2: Generate Number Sequence
**Difficulty**: Medium

Generate numbers from 1 to 100 using recursive CTE.

### Solution
```sql
WITH RECURSIVE numbers AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 100
)
SELECT n FROM numbers;
```

---

## Question 3: Generate Date Range
**Difficulty**: Medium

Generate all dates between two dates.

### Solution
```sql
WITH RECURSIVE date_range AS (
    SELECT DATE '2024-01-01' as date
    UNION ALL
    SELECT date + INTERVAL '1 day'
    FROM date_range
    WHERE date < DATE '2024-01-31'
)
SELECT date FROM date_range;
```

---

## Question 4: Find Path in Hierarchy
**Difficulty**: Hard

Find the path from an employee to the CEO.

### Solution
```sql
WITH RECURSIVE path_to_ceo AS (
    -- Anchor: Start with the employee
    SELECT employee_id, first_name, manager_id, 
           CAST(first_name AS VARCHAR(1000)) as path
    FROM employees
    WHERE employee_id = 7  -- Grace
    
    UNION ALL
    
    -- Recursive: Go up the hierarchy
    SELECT e.employee_id, e.first_name, e.manager_id,
           p.path || ' -> ' || e.first_name
    FROM employees e
    INNER JOIN path_to_ceo p ON e.employee_id = p.manager_id
)
SELECT path FROM path_to_ceo WHERE manager_id IS NULL;
```

### Output
```
path
Grace -> David -> Bob -> Alice
```

---

## Question 5: Bill of Materials
**Difficulty**: Hard

Given a product hierarchy, find all components needed to build a product.

### Table: product_components
| Column | Type |
|--------|------|
| parent_id | INT |
| component_id | INT |
| quantity | INT |

### Solution
```sql
WITH RECURSIVE bom AS (
    -- Anchor: Top-level product
    SELECT parent_id, component_id, quantity, 1 as level
    FROM product_components
    WHERE parent_id = 1  -- Product ID
    
    UNION ALL
    
    -- Recursive: Components of components
    SELECT pc.parent_id, pc.component_id, pc.quantity * bom.quantity, bom.level + 1
    FROM product_components pc
    INNER JOIN bom ON pc.parent_id = bom.component_id
)
SELECT component_id, SUM(quantity) as total_quantity
FROM bom
GROUP BY component_id;
```

---

## Key Concepts

- **Recursive CTE**: CTE that references itself
- **Anchor member**: Base case (non-recursive part)
- **Recursive member**: References the CTE itself
- **Termination**: Must have a condition to stop recursion

## Recursive CTE Structure
```sql
WITH RECURSIVE cte_name AS (
    -- Anchor member (base case)
    SELECT ...
    
    UNION ALL
    
    -- Recursive member
    SELECT ... FROM cte_name WHERE termination_condition
)
SELECT * FROM cte_name;
```

## Common Interview Questions

1. Find all subordinates of a manager
2. Generate sequence of numbers
3. Find path from node to root
3. Calculate bill of materials
4. Find all ancestors/descendants

## Practice Exercises

1. Find all categories in a category hierarchy
2. Generate Fibonacci sequence
3. Find all flights with connections
4. Calculate total cost in a product hierarchy