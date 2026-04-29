# Set Matrix Zeroes

## Problem

Given a matrix, if an element is `0`, set its entire row and column to `0` in-place.

## Input

- `matrix`: 2D list of integers

## Output

- Modify `matrix` in-place

## Example

```text
Input: [[1,1,1],[1,0,1],[1,1,1]]
Output: [[1,0,1],[0,0,0],[1,0,1]]
```

## Intuition

Use the first row and first column as markers. Track whether they originally contained zeroes separately.

## Solution

```python
def set_zeroes(matrix):
    rows, cols = len(matrix), len(matrix[0])
    first_row_zero = any(matrix[0][c] == 0 for c in range(cols))
    first_col_zero = any(matrix[r][0] == 0 for r in range(rows))

    for r in range(1, rows):
        for c in range(1, cols):
            if matrix[r][c] == 0:
                matrix[r][0] = 0
                matrix[0][c] = 0

    for r in range(1, rows):
        for c in range(1, cols):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0

    if first_row_zero:
        for c in range(cols):
            matrix[0][c] = 0

    if first_col_zero:
        for r in range(rows):
            matrix[r][0] = 0
```

## Complexity

- Time: `O(m * n)`
- Space: `O(1)`

