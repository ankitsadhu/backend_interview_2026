# Sudoku Solver

## Problem

Given a partially filled `9 x 9` Sudoku board, fill the empty cells so the board becomes valid. Empty cells are represented by `"."`.

## Input

- `board`: `9 x 9` grid of strings `"1"` to `"9"` or `"."`

## Output

- Modify `board` in-place

## Example

```text
Input:
[
  ["5","3",".",".","7",".",".",".","."],
  ["6",".",".","1","9","5",".",".","."],
  [".","9","8",".",".",".",".","6","."],
  ["8",".",".",".","6",".",".",".","3"],
  ["4",".",".","8",".","3",".",".","1"],
  ["7",".",".",".","2",".",".",".","6"],
  [".","6",".",".",".",".","2","8","."],
  [".",".",".","4","1","9",".",".","5"],
  [".",".",".",".","8",".",".","7","9"]
]

Output: board is filled with a valid Sudoku solution.
```

## Intuition

Try digits in empty cells, but keep row, column, and box sets so validity checks are fast.

## Solution

```python
def solve_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empty = []

    for r in range(9):
        for c in range(9):
            value = board[r][c]
            if value == ".":
                empty.append((r, c))
            else:
                rows[r].add(value)
                cols[c].add(value)
                boxes[(r // 3) * 3 + c // 3].add(value)

    def backtrack(i):
        if i == len(empty):
            return True

        r, c = empty[i]
        box = (r // 3) * 3 + c // 3

        for digit in "123456789":
            if digit in rows[r] or digit in cols[c] or digit in boxes[box]:
                continue

            board[r][c] = digit
            rows[r].add(digit)
            cols[c].add(digit)
            boxes[box].add(digit)

            if backtrack(i + 1):
                return True

            board[r][c] = "."
            rows[r].remove(digit)
            cols[c].remove(digit)
            boxes[box].remove(digit)

        return False

    backtrack(0)
```

## Complexity

- Time: `O(9^E)`, where `E` is the number of empty cells
- Space: `O(E)` recursion stack

