# Word Search

## Problem

Given an `m x n` board of characters and a word, return `True` if the word exists in the grid. Adjacent cells are horizontal or vertical. A cell cannot be used more than once in the same path.

## Input

- `board`: 2D list of characters
- `word`: string

## Output

- Boolean

## Example

```text
Input:
board = [
  ["A","B","C","E"],
  ["S","F","C","S"],
  ["A","D","E","E"]
]
word = "ABCCED"

Output: True
```

## Intuition

Start DFS from every matching first character. Mark a cell as visited while exploring, then unmark it when backtracking.

## Solution

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])

    def dfs(r, c, i):
        if i == len(word):
            return True
        if r < 0 or r == rows or c < 0 or c == cols:
            return False
        if board[r][c] != word[i]:
            return False

        saved = board[r][c]
        board[r][c] = "#"

        found = (
            dfs(r + 1, c, i + 1) or
            dfs(r - 1, c, i + 1) or
            dfs(r, c + 1, i + 1) or
            dfs(r, c - 1, i + 1)
        )

        board[r][c] = saved
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True

    return False
```

## Complexity

- Time: `O(m * n * 4^L)`, where `L = len(word)`
- Space: `O(L)` recursion stack

