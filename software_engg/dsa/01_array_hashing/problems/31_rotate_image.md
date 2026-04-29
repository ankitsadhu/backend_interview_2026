# Rotate Image

## Problem

Given an `n x n` matrix, rotate it 90 degrees clockwise in-place.

## Input

- `matrix`: square 2D list

## Output

- Modify `matrix` in-place

## Example

```text
Input: [[1,2,3],[4,5,6],[7,8,9]]
Output: [[7,4,1],[8,5,2],[9,6,3]]
```

## Intuition

Transpose the matrix, then reverse each row.

## Solution

```python
def rotate(matrix):
    n = len(matrix)

    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]

    for row in matrix:
        row.reverse()
```

## Complexity

- Time: `O(n^2)`
- Space: `O(1)`

