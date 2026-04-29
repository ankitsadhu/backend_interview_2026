# Guess Number Higher or Lower

## Problem

You need to guess a number from `1` to `n`. The API `guess(num)` returns `-1` if the picked number is lower, `1` if higher, and `0` if correct.

## Input

- `n`: upper bound
- `guess`: comparison API

## Output

- Picked number

## Example

```text
Input: n = 10, pick = 6
Output: 6
```

## Intuition

Use binary search and follow the API direction.

## Solution

```python
def guess_number(n):
    left, right = 1, n

    while left <= right:
        mid = left + (right - left) // 2
        result = guess(mid)

        if result == 0:
            return mid
        if result > 0:
            left = mid + 1
        else:
            right = mid - 1
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

