# Container With Most Water

## Problem

Given heights of vertical lines, return the maximum water area between two lines.

## Input

- `height`: list of non-negative integers

## Output

- Maximum area

## Example

```text
Input: height = [1,8,6,2,5,4,8,3,7]
Output: 49
```

## Intuition

The shorter line limits the area. Move the pointer at the shorter line because moving the taller one cannot improve the limiting height.

## Solution

```python
def max_area(height):
    left, right = 0, len(height) - 1
    best = 0

    while left < right:
        width = right - left
        best = max(best, width * min(height[left], height[right]))

        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

