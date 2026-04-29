# Game of Life

## Problem

Given a board representing Conway's Game of Life, compute the next state in-place.

## Input

- `board`: 2D list of `0`s and `1`s

## Output

- Modify `board` in-place

## Example

```text
Input: [[0,1,0],[0,0,1],[1,1,1],[0,0,0]]
Output: [[0,0,0],[1,0,1],[0,1,1],[0,1,0]]
```

## Intuition

Use temporary encoded states:

- `2`: live becomes dead
- `3`: dead becomes live

The original state is still recoverable while counting neighbors.

## Solution

```python
def game_of_life(board):
    rows, cols = len(board), len(board[0])
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]

    def live_neighbors(r, c):
        count = 0
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] in (1, 2):
                count += 1
        return count

    for r in range(rows):
        for c in range(cols):
            live = live_neighbors(r, c)
            if board[r][c] == 1 and (live < 2 or live > 3):
                board[r][c] = 2
            elif board[r][c] == 0 and live == 3:
                board[r][c] = 3

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 2:
                board[r][c] = 0
            elif board[r][c] == 3:
                board[r][c] = 1
```

## Complexity

- Time: `O(m * n)`
- Space: `O(1)`

