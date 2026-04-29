# N-Queens II

## Problem

Return the number of distinct ways to place `n` queens on an `n x n` chessboard so that no two queens attack each other.

## Input

- `n`: board size

## Output

- Count of valid arrangements

## Example

```text
Input: n = 4
Output: 2
```

## Intuition

Same constraints as N-Queens, but count solutions instead of building boards.

## Solution

```python
def total_n_queens(n):
    cols = set()
    diag = set()
    anti_diag = set()

    def backtrack(row):
        if row == n:
            return 1

        count = 0
        for col in range(n):
            if col in cols or row - col in diag or row + col in anti_diag:
                continue

            cols.add(col)
            diag.add(row - col)
            anti_diag.add(row + col)

            count += backtrack(row + 1)

            cols.remove(col)
            diag.remove(row - col)
            anti_diag.remove(row + col)

        return count

    return backtrack(0)
```

## Complexity

- Time: `O(n!)` approximate search space
- Space: `O(n)`

