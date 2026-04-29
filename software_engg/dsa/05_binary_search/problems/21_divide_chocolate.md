# Divide Chocolate

## Problem

Given sweetness values and integer `k`, split the chocolate into `k + 1` pieces. You take the piece with minimum sweetness, so maximize that minimum sweetness.

## Input

- `sweetness`: list of positive integers
- `k`: number of friends

## Output

- Maximum possible minimum sweetness

## Example

```text
Input: sweetness = [1,2,3,4,5,6,7,8,9], k = 5
Output: 6
```

## Intuition

If we can make at least `k + 1` pieces each with sweetness at least `x`, then `x` is feasible. Binary search the maximum feasible `x`.

## Solution

```python
def maximize_sweetness(sweetness, k):
    pieces_needed = k + 1
    left, right = 1, sum(sweetness) // pieces_needed

    def can(min_sweetness):
        pieces = 0
        current = 0

        for value in sweetness:
            current += value
            if current >= min_sweetness:
                pieces += 1
                current = 0

        return pieces >= pieces_needed

    while left <= right:
        mid = left + (right - left) // 2
        if can(mid):
            left = mid + 1
        else:
            right = mid - 1

    return right
```

## Complexity

- Time: `O(n log sum(sweetness))`
- Space: `O(1)`

