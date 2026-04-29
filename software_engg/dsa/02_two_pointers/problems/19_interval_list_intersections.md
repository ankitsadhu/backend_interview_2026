# Interval List Intersections

## Problem

Given two lists of closed intervals sorted by start time, return their intersections.

## Input

- `firstList`: sorted list of intervals
- `secondList`: sorted list of intervals

## Output

- List of intersecting intervals

## Example

```text
Input:
firstList = [[0,2],[5,10],[13,23],[24,25]]
secondList = [[1,5],[8,12],[15,24],[25,26]]

Output: [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
```

## Intuition

Two intervals overlap when `max(starts) <= min(ends)`. Move the pointer whose interval ends first.

## Solution

```python
def interval_intersection(firstList, secondList):
    i = j = 0
    ans = []

    while i < len(firstList) and j < len(secondList):
        start = max(firstList[i][0], secondList[j][0])
        end = min(firstList[i][1], secondList[j][1])

        if start <= end:
            ans.append([start, end])

        if firstList[i][1] < secondList[j][1]:
            i += 1
        else:
            j += 1

    return ans
```

## Complexity

- Time: `O(n + m)`
- Space: `O(1)` excluding output

