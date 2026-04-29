# Factorial

## Problem

Given a non-negative integer `n`, return `n!`.

## Input

- `n`: integer where `n >= 0`

## Output

- Factorial of `n`

## Example

```text
Input: n = 5
Output: 120
```

## Intuition

`n! = n * (n - 1)!`. Stop when `n` is `0` or `1`.

## Solution

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

