# Trapping Rain Water

## Problem

Given an elevation map, return how much rain water can be trapped.

## Input

- `height`: list of non-negative integers

## Output

- Units of trapped water

## Example

```text
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
```

## Intuition

Water at a position depends on the smaller of the best wall to its left and right. Move the side with the smaller current max.

## Solution

```python
def trap(height):
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0

    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1

    return water
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

