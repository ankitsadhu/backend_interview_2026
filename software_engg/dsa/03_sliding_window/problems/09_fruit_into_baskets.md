# Fruit Into Baskets

## Problem

Given an array `fruits`, return the length of the longest subarray containing at most two distinct fruit types.

## Input

- `fruits`: list of integers

## Output

- Maximum number of fruits collected

## Example

```text
Input: fruits = [1,2,1]
Output: 3
```

## Intuition

This is the longest window with at most two distinct values.

## Solution

```python
from collections import defaultdict

def total_fruit(fruits):
    count = defaultdict(int)
    left = 0
    best = 0

    for right, fruit in enumerate(fruits):
        count[fruit] += 1

        while len(count) > 2:
            count[fruits[left]] -= 1
            if count[fruits[left]] == 0:
                del count[fruits[left]]
            left += 1

        best = max(best, right - left + 1)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)` because at most three fruit types are tracked before shrinking

