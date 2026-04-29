# Boats to Save People

## Problem

Given people weights and a boat limit, return the minimum number of boats needed. Each boat can carry at most two people.

## Input

- `people`: list of weights
- `limit`: boat weight limit

## Output

- Minimum number of boats

## Example

```text
Input: people = [3,2,2,1], limit = 3
Output: 3
```

## Intuition

Sort weights. Always place the heaviest remaining person. If the lightest can fit with them, pair them.

## Solution

```python
def num_rescue_boats(people, limit):
    people.sort()
    left, right = 0, len(people) - 1
    boats = 0

    while left <= right:
        if people[left] + people[right] <= limit:
            left += 1
        right -= 1
        boats += 1

    return boats
```

## Complexity

- Time: `O(n log n)`
- Space: `O(1)` excluding sort stack

