# Window Functions: Running Totals and Moving Averages

## Question 1: Running Total
**Difficulty**: Medium

Calculate the running total of sales by date.

### Table: sales
| Column | Type |
|--------|------|
| sale_id | INT (PK) |
| sale_date | DATE |
| amount | DECIMAL(10,2) |

### Sample Data
```
sale_id | sale_date  | amount
1       | 2024-01-01 | 100
2       | 2024-01-02 | 150
3       | 2024-01-03 | 200
4       | 2024-01-04 | 120
5       | 2024-01-05 | 180
```

### Solution
```sql
SELECT sale_date, amount,
       SUM(amount) OVER (ORDER BY sale_date) as running_total
FROM sales
ORDER BY sale_date;
```

### Output
```
sale_date  | amount | running_total
2024-01-01 | 100    | 100
2024-01-02 | 150    | 250
2024-01-03 | 200    | 450
2024-01-04 | 120    | 570
2024-01-05 | 180    | 750
```

---

## Question 2: Running Total by Category
**Difficulty**: Medium

Calculate running total of sales per product category.

### Solution
```sql
SELECT category, sale_date, amount,
       SUM(amount) OVER (PARTITION BY category ORDER BY sale_date) as category_running_total
FROM sales
ORDER BY category, sale_date;
```

---

## Question 3: Moving Average
**Difficulty**: Hard

Calculate the 3-day moving average of sales.

### Solution
```sql
SELECT sale_date, amount,
       AVG(amount) OVER (
           ORDER BY sale_date 
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ) as moving_avg_3day
FROM sales
ORDER BY sale_date;
```

### Output
```
sale_date  | amount | moving_avg_3day
2024-01-01 | 100    | 100.00
2024-01-02 | 150    | 125.00
2024-01-03 | 200    | 150.00
2024-01-04 | 120    | 156.67
2024-01-05 | 180    | 166.67
```

---

## Question 4: Cumulative Distribution
**Difficulty**: Hard

Calculate the cumulative percentage of total sales.

### Solution
```sql
SELECT sale_date, amount,
       SUM(amount) OVER (ORDER BY sale_date) as running_total,
       SUM(amount) OVER () as grand_total,
       ROUND(
           SUM(amount) OVER (ORDER BY sale_date) * 100.0 / 
           SUM(amount) OVER (), 2
       ) as cumulative_pct
FROM sales
ORDER BY sale_date;
```

---

## Question 5: Year-to-Date (YTD) Total
**Difficulty**: Hard

Calculate year-to-date running total.

### Solution
```sql
SELECT sale_date, amount,
       SUM(amount) OVER (
           PARTITION BY YEAR(sale_date) 
           ORDER BY sale_date
       ) as ytd_total
FROM sales
ORDER BY sale_date;
```

---

## Key Concepts

- **SUM() OVER**: Running total when ordered
- **ROWS BETWEEN**: Define window frame
- **PARTITION BY**: Reset running total per group
- **UNBOUNDED PRECEDING**: From start of partition

## Window Frame Syntax
```sql
SUM(col) OVER (
    PARTITION BY ...
    ORDER BY ...
    ROWS BETWEEN n PRECEDING AND m FOLLOWING
)
```

## Common Frame Options
```
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  -- All previous + current
ROWS BETWEEN 2 PRECEDING AND CURRENT ROW          -- Last 3 rows
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING  -- Current + all after
ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING          -- Previous, current, next
```

## Common Interview Questions

1. Calculate running total of transactions
2. Find 7-day moving average
3. Calculate cumulative percentage
4. Find YTD and MTD totals

## Practice Exercises

1. Calculate running average of test scores
2. Find 30-day moving average of stock prices
3. Calculate month-to-date sales total
4. Find cumulative distribution of salaries