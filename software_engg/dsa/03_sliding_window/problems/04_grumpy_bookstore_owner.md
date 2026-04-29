# Grumpy Bookstore Owner

## Problem

Given arrays `customers` and `grumpy`, and integer `minutes`, choose one window of length `minutes` where the owner is not grumpy. Return the maximum satisfied customers.

## Input

- `customers`: customers at each minute
- `grumpy`: `1` if owner is grumpy, else `0`
- `minutes`: window length

## Output

- Maximum satisfied customers

## Example

```text
Input: customers = [1,0,1,2,1,1,7,5], grumpy = [0,1,0,1,0,1,0,1], minutes = 3
Output: 16
```

## Intuition

Customers are already satisfied when `grumpy[i] == 0`. The chosen window adds extra satisfied customers only where `grumpy[i] == 1`.

## Solution

```python
def max_satisfied(customers, grumpy, minutes):
    base = 0
    extra = 0

    for i in range(len(customers)):
        if grumpy[i] == 0:
            base += customers[i]

    for i in range(minutes):
        if grumpy[i] == 1:
            extra += customers[i]

    best_extra = extra
    for right in range(minutes, len(customers)):
        if grumpy[right] == 1:
            extra += customers[right]
        left = right - minutes
        if grumpy[left] == 1:
            extra -= customers[left]
        best_extra = max(best_extra, extra)

    return base + best_extra
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

