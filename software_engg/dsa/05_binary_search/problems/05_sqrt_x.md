# Sqrt(x)

## Problem

Given a non-negative integer `x`, return the integer square root of `x`.

## Input

- `x`: non-negative integer

## Output

- Floor of `sqrt(x)`

## Example

```text
Input: x = 8
Output: 2
```

## Intuition

Search for the largest integer `m` where `m * m <= x`.

## Solution

```python
def my_sqrt(x):
    left, right = 0, x
    ans = 0

    while left <= right:
        mid = left + (right - left) // 2
        square = mid * mid

        if square <= x:
            ans = mid
            left = mid + 1
        else:
            right = mid - 1

    return ans
```

## Complexity

- Time: `O(log x)`
- Space: `O(1)`

