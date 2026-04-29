# Capacity To Ship Packages Within D Days

## Problem

Given package weights and `days`, return the minimum ship capacity needed to ship all packages within `days`, preserving order.

## Input

- `weights`: list of package weights
- `days`: number of days

## Output

- Minimum feasible capacity

## Example

```text
Input: weights = [1,2,3,4,5,6,7,8,9,10], days = 5
Output: 15
```

## Intuition

Capacity must be at least the heaviest package and at most the total weight. Check whether a capacity can finish within `days`.

## Solution

```python
def ship_within_days(weights, days):
    left, right = max(weights), sum(weights)

    def can(capacity):
        used_days = 1
        load = 0

        for weight in weights:
            if load + weight > capacity:
                used_days += 1
                load = 0
            load += weight

        return used_days <= days

    while left < right:
        mid = left + (right - left) // 2
        if can(mid):
            right = mid
        else:
            left = mid + 1

    return left
```

## Complexity

- Time: `O(n log sum(weights))`
- Space: `O(1)`

