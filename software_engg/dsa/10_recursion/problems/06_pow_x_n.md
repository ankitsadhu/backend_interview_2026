# pow(x, n)

## Problem

Implement `pow(x, n)`, which calculates `x` raised to integer power `n`.

## Input

- `x`: floating-point number
- `n`: integer, can be negative

## Output

- `x^n`

## Example

```text
Input: x = 2.0, n = 10
Output: 1024.0
```

## Intuition

Use fast exponentiation. Compute half power once, then square it.

## Solution

```python
def my_pow(x, n):
    def fast_power(power):
        if power == 0:
            return 1

        half = fast_power(power // 2)
        result = half * half
        if power % 2 == 1:
            result *= x
        return result

    ans = fast_power(abs(n))
    return ans if n >= 0 else 1 / ans
```

## Complexity

- Time: `O(log n)`
- Space: `O(log n)`

