# Remove K Digits

## Problem

Given a numeric string `num` and integer `k`, remove `k` digits so the remaining number is smallest possible.

## Input

- `num`: numeric string
- `k`: number of digits to remove

## Output

- Smallest possible number as a string

## Example

```text
Input: num = "1432219", k = 3
Output: "1219"
```

## Intuition

To make the number smaller, remove previous larger digits when a smaller digit appears. This creates a monotonic increasing stack.

## Solution

```python
def remove_kdigits(num, k):
    stack = []

    for digit in num:
        while k > 0 and stack and stack[-1] > digit:
            stack.pop()
            k -= 1
        stack.append(digit)

    while k > 0:
        stack.pop()
        k -= 1

    result = "".join(stack).lstrip("0")
    return result if result else "0"
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

