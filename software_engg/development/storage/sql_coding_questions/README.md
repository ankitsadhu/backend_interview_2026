# SQL Coding Questions - Complete Guide

This directory contains comprehensive SQL coding questions and solutions organized by topic and difficulty. Questions are arranged in a logical learning order from fundamentals to advanced concepts.

## Table of Contents

### 1. Basic SELECT & Filtering (Foundation)
| # | Topic | Solution |
|---|-------|----------|
| 1.1 | SELECT, WHERE, ORDER BY | [Solutions](problems/01_basic_select.md) |
| 1.2 | DISTINCT, LIMIT, OFFSET | [Solutions](problems/02_distinct_limit.md) |
| 1.3 | LIKE, IN, BETWEEN | [Solutions](problems/03_like_in_between.md) |
| 1.4 | NULL handling (IS NULL, COALESCE) | [Solutions](problems/04_null_handling.md) |

### 2. Aggregation & Grouping
| # | Topic | Solution |
|---|-------|----------|
| 2.1 | COUNT, SUM, AVG, MIN, MAX | [Solutions](problems/05_aggregation_basics.md) |
| 2.2 | GROUP BY | [Solutions](problems/06_group_by.md) |
| 2.3 | HAVING clause | [Solutions](problems/07_having_clause.md) |
| 2.4 | GROUP BY with multiple columns | [Solutions](problems/08_group_by_multiple.md) |

### 3. JOINS (Critical Topic)
| # | Topic | Solution |
|---|-------|----------|
| 3.1 | INNER JOIN | [Solutions](problems/09_inner_join.md) |
| 3.2 | LEFT JOIN / RIGHT JOIN | [Solutions](problems/10_left_right_join.md) |
| 3.3 | FULL OUTER JOIN | [Solutions](problems/11_full_outer_join.md) |
| 3.4 | SELF JOIN | [Solutions](problems/12_self_join.md) |
| 3.5 | CROSS JOIN | [Solutions](problems/13_cross_join.md) |
| 3.6 | Multiple JOINs | [Solutions](problems/14_multiple_joins.md) |
| 3.7 | JOIN with aggregation | [Solutions](problems/15_join_with_aggregation.md) |

### 4. Subqueries
| # | Topic | Solution |
|---|-------|----------|
| 4.1 | Subquery in WHERE | [Solutions](problems/16_subquery_where.md) |
| 4.2 | Subquery in SELECT | [Solutions](problems/17_subquery_select.md) |
| 4.3 | Subquery in FROM | [Solutions](problems/18_subquery_from.md) |
| 4.4 | Correlated Subqueries | [Solutions](problems/19_correlated_subquery.md) |
| 4.5 | EXISTS / NOT EXISTS | [Solutions](problems/20_exists_not_exists.md) |
| 4.6 | ANY / ALL operators | [Solutions](problems/21_any_all_operators.md) |

### 5. Window Functions (Advanced)
| # | Topic | Solution |
|---|-------|----------|
| 5.1 | ROW_NUMBER() | [Solutions](problems/22_row_number.md) |
| 5.2 | RANK(), DENSE_RANK(), NTILE() | [Solutions](problems/23_rank_functions.md) |
| 5.3 | LAG(), LEAD() | [Solutions](problems/24_lag_lead.md) |
| 5.4 | Running totals with SUM() OVER | [Solutions](problems/25_running_totals.md) |
| 5.5 | PARTITION BY | [Solutions](problems/26_partition_by.md) |
| 5.6 | FIRST_VALUE(), LAST_VALUE(), NTH_VALUE() | [Solutions](problems/27_value_functions.md) |
| 5.7 | Complex window problems | [Solutions](problems/28_window_complex.md) |

### 6. CTE & Recursive CTE
| # | Topic | Solution |
|---|-------|----------|
| 6.1 | Basic CTE (WITH clause) | [Solutions](problems/29_cte_basics.md) |
| 6.2 | Multiple CTEs | [Solutions](problems/30_multiple_ctes.md) |
| 6.3 | Recursive CTE for hierarchies | [Solutions](problems/31_recursive_cte.md) |
| 6.4 | Recursive CTE for sequences | [Solutions](problems/32_recursive_sequences.md) |

### 7. Date & Time Functions
| # | Topic | Solution |
|---|-------|----------|
| 7.1 | DATE, TIME, DATETIME types | [Solutions](problems/33_date_types.md) |
| 7.2 | DATE arithmetic | [Solutions](problems/34_date_arithmetic.md) |
| 7.3 | DATE formatting | [Solutions](problems/35_date_formatting.md) |
| 7.4 | Date ranges & gaps | [Solutions](problems/36_date_ranges.md) |
| 7.5 | Time-based aggregations | [Solutions](problems/37_time_aggregation.md) |

### 8. String Functions
| # | Topic | Solution |
|---|-------|----------|
| 8.1 | CONCAT, SUBSTRING, TRIM | [Solutions](problems/38_string_basics.md) |
| 8.2 | REPLACE, UPPER, LOWER | [Solutions](problems/39_string_functions.md) |
| 8.3 | STRING_AGG / GROUP_CONCAT | [Solutions](problems/40_string_aggregation.md) |

### 9. Advanced SQL Patterns
| # | Topic | Solution |
|---|-------|----------|
| 9.1 | PIVOT / UNPIVOT | [Solutions](problems/41_pivot_unpivot.md) |
| 9.2 | Gaps and Islands | [Solutions](problems/42_gaps_islands.md) |
| 9.3 | Top N per group | [Solutions](problems/43_top_n_per_group.md) |
| 9.4 | Median calculation | [Solutions](problems/44_median.md) |
| 9.5 | Percentile calculation | [Solutions](problems/45_percentile.md) |

### 10. Database Design & Optimization
| # | Topic | Solution |
|---|-------|----------|
| 10.1 | Indexing strategies | [Solutions](problems/46_indexing.md) |
| 10.2 | Query optimization with EXPLAIN | [Solutions](problems/47_explain.md) |
| 10.3 | N+1 problem solutions | [Solutions](problems/48_n_plus_1.md) |
| 10.4 | Pagination techniques | [Solutions](problems/49_pagination.md) |

### 11. Transactions & Concurrency
| # | Topic | Solution |
|---|-------|----------|
| 11.1 | ACID properties | [Solutions](problems/50_acid.md) |
| 11.2 | Transaction isolation levels | [Solutions](problems/51_isolation_levels.md) |
| 11.3 | Locking mechanisms | [Solutions](problems/52_locking.md) |
| 11.4 | Deadlock prevention | [Solutions](problems/53_deadlock.md) |

### 12. Stored Procedures & Functions
| # | Topic | Solution |
|---|-------|----------|
| 12.1 | Creating stored procedures | [Solutions](problems/54_stored_procedures.md) |
| 12.2 | User-defined functions | [Solutions](problems/55_udf.md) |
| 12.3 | Triggers | [Solutions](problems/56_triggers.md) |

## Common Table Schemas for Practice

### Employees Table
```sql
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    department_id INT,
    salary DECIMAL(10,2),
    hire_date DATE,
    manager_id INT
);

CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100),
    location VARCHAR(100)
);
```

### Orders & Customers
```sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    signup_date DATE
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2),
    status VARCHAR(20)
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);
```

## Study Order Recommendation

1. **Week 1-2**: Basic SELECT, Filtering, Aggregation
2. **Week 3-4**: JOINS (most important for interviews)
3. **Week 5**: Subqueries
4. **Week 6-7**: Window Functions
5. **Week 8**: CTE and advanced patterns
6. **Week 9**: Date/Time and String functions
7. **Week 10**: Database design and optimization

## Interview Tips

- **Practice on LeetCode/HackerRank**: Apply these concepts
- **Understand execution order**: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY
- **Know your database**: Syntax varies between MySQL, PostgreSQL, SQL Server
- **Think about edge cases**: NULL values, empty results, duplicates

## Related Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [SQLZoo](https://sqlzoo.net/) - Interactive SQL practice