# Spiral Matrix

## Problem

Given an `m x n` matrix, return all elements in spiral order.

## Input

- `matrix`: 2D list

## Output

- Elements in spiral order

## Example

```text
Input: [[1,2,3],[4,5,6],[7,8,9]]
Output: [1,2,3,6,9,8,7,4,5]
```

## Intuition

Maintain four boundaries: top, bottom, left, and right. Shrink them after traversing each side.

## Solution

```python
def spiral_order(matrix):
    ans = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            ans.append(matrix[top][c])
        top += 1

        for r in range(top, bottom + 1):
            ans.append(matrix[r][right])
        right -= 1

        if top <= bottom:
            for c in range(right, left - 1, -1):
                ans.append(matrix[bottom][c])
            bottom -= 1

        if left <= right:
            for r in range(bottom, top - 1, -1):
                ans.append(matrix[r][left])
            left += 1

    return ans
```

## Complexity

- Time: `O(m * n)`
- Space: `O(1)` excluding output

