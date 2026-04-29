# Best Time to Buy and Sell Stock

## Problem

Given stock prices, return the maximum profit from one buy and one sell.

## Input

- `prices`: list of integers

## Output

- Maximum profit

## Example

```text
Input: prices = [7,1,5,3,6,4]
Output: 5
```

## Intuition

Treat the buy day as the left side of a window and the sell day as the right side. Keep the lowest buy price seen so far.

## Solution

```python
def max_profit(prices):
    min_price = float("inf")
    best = 0

    for price in prices:
        min_price = min(min_price, price)
        best = max(best, price - min_price)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

