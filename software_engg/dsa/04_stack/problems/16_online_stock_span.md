# Online Stock Span

## Problem

Design a class that returns the stock span for each incoming price. The span is the number of consecutive days up to today where the price was less than or equal to today's price.

## Input

- Stream of prices

## Output

- Span for each price

## Example

```text
next(100) -> 1
next(80) -> 1
next(60) -> 1
next(70) -> 2
next(60) -> 1
next(75) -> 4
next(85) -> 6
```

## Intuition

Keep a decreasing stack of `(price, span)`. When current price is greater than previous prices, merge their spans.

## Solution

```python
class StockSpanner:
    def __init__(self):
        self.stack = []

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span
```

## Complexity

- Time: amortized `O(1)` per call
- Space: `O(n)`

