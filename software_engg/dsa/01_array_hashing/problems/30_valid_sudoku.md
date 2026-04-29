# Valid Sudoku

## Problem

Determine if a partially filled `9 x 9` Sudoku board is valid. Empty cells are `"."`.

## Input

- `board`: `9 x 9` grid of strings

## Output

- Boolean

## Example

```text
Input: valid partial Sudoku board
Output: True
```

## Intuition

Each digit must be unique within its row, column, and `3 x 3` box.

## Solution

```python
def is_valid_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]

    for r in range(9):
        for c in range(9):
            value = board[r][c]
            if value == ".":
                continue

            box = (r // 3) * 3 + c // 3
            if value in rows[r] or value in cols[c] or value in boxes[box]:
                return False

            rows[r].add(value)
            cols[c].add(value)
            boxes[box].add(value)

    return True
```

## Complexity

- Time: `O(1)` because the board is fixed size
- Space: `O(1)`

