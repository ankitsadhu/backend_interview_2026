# Koko Eating Bananas

## Problem

Given banana piles and integer `h`, return the minimum eating speed `k` so Koko can finish all piles within `h` hours.

## Input

- `piles`: list of pile sizes
- `h`: hours available

## Output

- Minimum feasible speed

## Example

```text
Input: piles = [3,6,7,11], h = 8
Output: 4
```

## Intuition

If Koko can finish at speed `k`, she can also finish at any faster speed. Binary search the minimum feasible speed.

## Solution

```python
import math

def min_eating_speed(piles, h):
    left, right = 1, max(piles)

    def can(speed):
        hours = 0
        for pile in piles:
            hours += math.ceil(pile / speed)
        return hours <= h

    while left < right:
        mid = left + (right - left) // 2
        if can(mid):
            right = mid
        else:
            left = mid + 1

    return left
```

## Complexity

- Time: `O(n log max(piles))`
- Space: `O(1)`

