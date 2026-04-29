# Largest Rectangle in Histogram

## Problem

Given bar heights in a histogram, return the area of the largest rectangle.

## Input

- `heights`: list of non-negative integers

## Output

- Maximum rectangle area

## Example

```text
Input: heights = [2,1,5,6,2,3]
Output: 10
```

## Intuition

Use an increasing stack of indices. When a shorter bar appears, it gives the right boundary for taller bars on the stack.

## Solution

```python
def largest_rectangle_area(heights):
    stack = []
    best = 0
    heights.append(0)

    for i, height in enumerate(heights):
        while stack and heights[stack[-1]] > height:
            h = heights[stack.pop()]
            left_boundary = stack[-1] if stack else -1
            width = i - left_boundary - 1
            best = max(best, h * width)
        stack.append(i)

    heights.pop()
    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

