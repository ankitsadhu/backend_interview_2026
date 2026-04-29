# Print Numbers Recursively

## Problem

Given an integer `n`, print numbers from `1` to `n` using recursion.

## Input

- `n`: positive integer

## Output

- Numbers from `1` to `n`

## Example

```text
Input: n = 5
Output: 1 2 3 4 5
```

## Intuition

To print in increasing order, first solve the smaller problem `n - 1`, then print `n`.

## Solution

```python
def print_numbers(n):
    if n == 0:
        return

    print_numbers(n - 1)
    print(n)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)` recursion stack

