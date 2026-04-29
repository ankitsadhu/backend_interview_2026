# Search a 2D Matrix

## Problem

Given an `m x n` matrix where each row is sorted and the first value of each row is greater than the last value of the previous row, return whether `target` exists.

## Input

- `matrix`: sorted 2D list
- `target`: integer

## Output

- Boolean

## Example

```text
Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
Output: True
```

## Intuition

Treat the matrix as one flattened sorted array. Convert a virtual index to row and column using division and modulo.

## Solution

```python
def search_matrix(matrix, target):
    rows, cols = len(matrix), len(matrix[0])
    left, right = 0, rows * cols - 1

    while left <= right:
        mid = left + (right - left) // 2
        r, c = divmod(mid, cols)
        value = matrix[r][c]

        if value == target:
            return True
        if value < target:
            left = mid + 1
        else:
            right = mid - 1

    return False
```

## Complexity

- Time: `O(log(m * n))`
- Space: `O(1)`

