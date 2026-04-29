# Valid Perfect Square

## Problem

Given a positive integer `num`, return `True` if it is a perfect square.

## Input

- `num`: positive integer

## Output

- Boolean

## Example

```text
Input: num = 16
Output: True
```

## Intuition

Binary search possible square roots and compare `mid * mid` with `num`.

## Solution

```python
def is_perfect_square(num):
    left, right = 1, num

    while left <= right:
        mid = left + (right - left) // 2
        square = mid * mid

        if square == num:
            return True
        if square < num:
            left = mid + 1
        else:
            right = mid - 1

    return False
```

## Complexity

- Time: `O(log num)`
- Space: `O(1)`

