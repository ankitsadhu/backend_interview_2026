# Window Functions: LAG() and LEAD()

## Question 1: Basic LAG()
**Difficulty**: Medium

Given a `sales` table, show each month's sales along with the previous month's sales.

### Table: sales
| Column | Type |
|--------|------|
| sale_id | INT (PK) |
| sale_date | DATE |
| amount | DECIMAL(10,2) |

### Sample Data
```
sale_id | sale_date  | amount
1       | 2024-01-01 | 1000
2       | 2024-02-01 | 1500
3       | 2024-03-01 | 1200
4       | 2024-04-01 | 1800
```

### Solution
```sql
SELECT sale_date, amount,
       LAG(amount) OVER (ORDER BY sale_date) as prev_month_sales
FROM sales;
```

### Output
```
sale_date  | amount | prev_month_sales
2024-01-01 | 1000   | NULL
2024-02-01 | 1500   | 1000
2024-03-01 | 1200   | 1500
2024-04-01 | 1800   | 1200
```

---

## Question 2: Basic LEAD()
**Difficulty**: Medium

Show each month's sales along with the next month's sales.

### Solution
```sql
SELECT sale_date, amount,
       LEAD(amount) OVER (ORDER BY sale_date) as next_month_sales
FROM sales;
```

---

## Question 3: Calculate Growth/Month-over-Month
**Difficulty**: Hard

Calculate the month-over-month growth percentage.

### Solution
```sql
SELECT sale_date, amount,
       LAG(amount) OVER (ORDER BY sale_date) as prev_amount,
       ROUND(
           (amount - LAG(amount) OVER (ORDER BY sale_date)) * 100.0 / 
           LAG(amount) OVER (ORDER BY sale_date), 2
       ) as growth_pct
FROM sales;
```

---

## Question 4: LAG with PARTITION BY
**Difficulty**: Hard

Show each employee's salary compared to the previous employee in the same department.

### Solution
```sql
SELECT first_name, department_id, salary,
       LAG(salary) OVER (PARTITION BY department_id ORDER BY salary) as prev_salary
FROM employees;
```

---

## Question 5: Multiple LAG/LEAD
**Difficulty**: Hard

Show current, previous, and next 2 months' sales.

### Solution
```sql
SELECT sale_date, amount,
       LAG(amount, 2) OVER (ORDER BY sale_date) as two_months_ago,
       LAG(amount, 1) OVER (ORDER BY sale_date) as last_month,
       amount as current_month,
       LEAD(amount, 1) OVER (ORDER BY sale_date) as next_month,
       LEAD(amount, 2) OVER (ORDER BY sale_date) as two_months_later
FROM sales;
```

---

## Key Concepts

- **LAG(column, offset)**: Access previous row's value
- **LEAD(column, offset)**: Access next row's value
- **Default offset**: 1 (previous/next row)
- **Default value**: NULL if no previous/next row

## LAG/LEAD Syntax
```sql
LAG(column, offset, default_value) OVER (
    PARTITION BY ... 
    ORDER BY ...
)
```

## Common Use Cases

1. **Month-over-month comparison**: Compare with previous period
2. **Running differences**: Calculate change from previous value
3. **Gap detection**: Find missing sequences
4. **Trend analysis**: Compare with multiple previous periods

## Common Interview Questions

1. Calculate day-over-day change in stock prices
2. Find consecutive days with increasing temperature
3. Compare current salary with previous employee's salary
4. Find gaps in sequential numbers

## Practice Exercises

1. Find months where sales decreased from previous month
2. Calculate 3-month moving average
3. Find employees earning more than the previous hire
4. Compare each day's temperature with same day last year