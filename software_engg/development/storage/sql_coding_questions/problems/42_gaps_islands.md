# Gaps and Islands Pattern

## Question 1: Find Gaps in Sequence
**Difficulty**: Hard

Given a table of booked seat numbers, find all available seat numbers (gaps).

### Table: bookings
| Column | Type |
|--------|------|
| booking_id | INT (PK) |
| seat_number | INT |

### Sample Data
```
booking_id | seat_number
1          | 1
2          | 2
3          | 3
4          | 7
5          | 8
6          | 10
```

### Solution
```sql
WITH numbered AS (
    SELECT seat_number,
           ROW_NUMBER() OVER (ORDER BY seat_number) as rn
    FROM bookings
),
groups AS (
    SELECT seat_number,
           seat_number - rn as grp
    FROM numbered
),
ranges AS (
    SELECT MIN(seat_number) as start_seat,
           MAX(seat_number) as end_seat
    FROM groups
    GROUP BY grp
)
SELECT start_seat, end_seat
FROM ranges
ORDER BY start_seat;
```

### Output (Islands)
```
start_seat | end_seat
1          | 3
7          | 8
10         | 10
```

### Gaps (Available seats)
```sql
WITH numbered AS (
    SELECT seat_number,
           ROW_NUMBER() OVER (ORDER BY seat_number) as rn
    FROM bookings
),
groups AS (
    SELECT seat_number,
           seat_number - rn as grp
    FROM numbered
),
ranges AS (
    SELECT MIN(seat_number) as start_seat,
           MAX(seat_number) as end_seat
    FROM groups
    GROUP BY grp
)
SELECT end_seat + 1 as gap_start,
       LEAD(start_seat) OVER (ORDER BY start_seat) - 1 as gap_end
FROM ranges
WHERE LEAD(start_seat) OVER (ORDER BY start_seat) - end_seat > 1;
```

---

## Question 2: Consecutive Numbers
**Difficulty**: Hard

Find all numbers that appear at least three times consecutively.

### Table: logs
| Column | Type |
|--------|------|
| id | INT (PK) |
| num | INT |

### Sample Data
```
id | num
1  | 1
2  | 1
3  | 1
4  | 2
5  | 1
6  | 2
7  | 2
```

### Solution
```sql
WITH numbered AS (
    SELECT id, num,
           ROW_NUMBER() OVER (ORDER BY id) as rn,
           ROW_NUMBER() OVER (PARTITION BY num ORDER BY id) as num_rn
    FROM logs
),
groups AS (
    SELECT num,
           id - num_rn as grp
    FROM numbered
)
SELECT DISTINCT num as ConsecutiveNums
FROM groups
GROUP BY num, grp
HAVING COUNT(*) >= 3;
```

---

## Question 3: Active User Streaks
**Difficulty**: Hard

Find users who have been active for at least 5 consecutive days.

### Table: user_activity
| Column | Type |
|--------|------|
| user_id | INT |
| activity_date | DATE |

### Solution
```sql
WITH numbered AS (
    SELECT user_id, activity_date,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date) as rn
    FROM user_activity
),
groups AS (
    SELECT user_id, activity_date,
           DATEADD(day, -rn, activity_date) as grp  -- or activity_date - rn * INTERVAL '1 day'
    FROM numbered
)
SELECT user_id, MIN(activity_date) as streak_start, MAX(activity_date) as streak_end
FROM groups
GROUP BY user_id, grp
HAVING COUNT(*) >= 5;
```

---

## Question 4: Find Missing Dates
**Difficulty**: Medium

Find all missing dates in a date range.

### Solution
```sql
WITH RECURSIVE date_range AS (
    SELECT MIN(activity_date) as date
    FROM user_activity
    UNION ALL
    SELECT date + INTERVAL '1 day'
    FROM date_range
    WHERE date < (SELECT MAX(activity_date) FROM user_activity)
)
SELECT dr.date as missing_date
FROM date_range dr
LEFT JOIN user_activity ua ON dr.date = ua.activity_date
WHERE ua.activity_date IS NULL;
```

---

## Key Concepts

- **Gaps**: Missing values in a sequence
- **Islands**: Consecutive values in a sequence
- **ROW_NUMBER trick**: `value - ROW_NUMBER()` creates groups for consecutive values
- **Group by difference**: Same difference = same island

## Island Detection Pattern
```sql
WITH numbered AS (
    SELECT value,
           ROW_NUMBER() OVER (ORDER BY value) as rn
    FROM table
),
groups AS (
    SELECT value,
           value - rn as grp  -- Same grp = same island
    FROM numbered
)
SELECT MIN(value) as island_start, MAX(value) as island_end
FROM groups
GROUP BY grp;
```

## Common Interview Questions

1. Find consecutive available seats
2. Find users with N consecutive login days
3. Find gaps in invoice numbers
4. Find longest consecutive sequence

## Practice Exercises

1. Find all available time slots in a booking system
2. Find employees with consecutive working days
3. Find missing sequence numbers in orders
4. Find longest streak of increasing stock prices