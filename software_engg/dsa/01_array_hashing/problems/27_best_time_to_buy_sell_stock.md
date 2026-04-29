# Best Time to Buy and Sell Stock

## Problem

Given stock prices where `prices[i]` is the price on day `i`, return the maximum profit from one buy and one sell.

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

Track the lowest price seen so far and calculate profit if selling today.

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

