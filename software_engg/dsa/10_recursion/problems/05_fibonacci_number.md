# Fibonacci Number

## Problem

Given `n`, return the `n`th Fibonacci number where `F(0) = 0` and `F(1) = 1`.

## Input

- `n`: non-negative integer

## Output

- `F(n)`

## Example

```text
Input: n = 6
Output: 8
```

## Intuition

Plain recursion repeats work. Memoization stores already solved values.

## Solution

```python
def fib(n):
    memo = {}

    def dfs(x):
        if x <= 1:
            return x
        if x in memo:
            return memo[x]

        memo[x] = dfs(x - 1) + dfs(x - 2)
        return memo[x]

    return dfs(n)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

