# Spiral Matrix II

## Problem

Given `n`, generate an `n x n` matrix filled with numbers from `1` to `n^2` in spiral order.

## Input

- `n`: matrix size

## Output

- Filled matrix

## Example

```text
Input: n = 3
Output: [[1,2,3],[8,9,4],[7,6,5]]
```

## Intuition

Use the same four-boundary traversal as Spiral Matrix, but write values instead of reading them.

## Solution

```python
def generate_matrix(n):
    matrix = [[0] * n for _ in range(n)]
    top, bottom = 0, n - 1
    left, right = 0, n - 1
    value = 1

    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            matrix[top][c] = value
            value += 1
        top += 1

        for r in range(top, bottom + 1):
            matrix[r][right] = value
            value += 1
        right -= 1

        for c in range(right, left - 1, -1):
            matrix[bottom][c] = value
            value += 1
        bottom -= 1

        for r in range(bottom, top - 1, -1):
            matrix[r][left] = value
            value += 1
        left += 1

    return matrix
```

## Complexity

- Time: `O(n^2)`
- Space: `O(n^2)` for output

