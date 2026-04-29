# N-Queens

## Problem

Place `n` queens on an `n x n` chessboard so that no two queens attack each other. Return all valid boards.

## Input

- `n`: board size

## Output

- List of board configurations

## Example

```text
Input: n = 4
Output:
[
  [".Q..", "...Q", "Q...", "..Q."],
  ["..Q.", "Q...", "...Q", ".Q.."]
]
```

## Intuition

Place one queen per row. A square is safe if its column, main diagonal, and anti-diagonal are unused.

## Solution

```python
def solve_n_queens(n):
    ans = []
    board = [["."] * n for _ in range(n)]
    cols = set()
    diag = set()       # row - col
    anti_diag = set()  # row + col

    def backtrack(row):
        if row == n:
            ans.append(["".join(r) for r in board])
            return

        for col in range(n):
            if col in cols or row - col in diag or row + col in anti_diag:
                continue

            board[row][col] = "Q"
            cols.add(col)
            diag.add(row - col)
            anti_diag.add(row + col)

            backtrack(row + 1)

            board[row][col] = "."
            cols.remove(col)
            diag.remove(row - col)
            anti_diag.remove(row + col)

    backtrack(0)
    return ans
```

## Complexity

- Time: `O(n!)` approximate search space
- Space: `O(n^2)` for board plus `O(n)` recursion state

