# Maximal Rectangle

## Problem

Given a binary matrix, return the area of the largest rectangle containing only `1`s.

## Input

- `matrix`: 2D list of `"0"` and `"1"`

## Output

- Maximum rectangle area

## Example

```text
Input:
matrix = [
  ["1","0","1","0","0"],
  ["1","0","1","1","1"],
  ["1","1","1","1","1"],
  ["1","0","0","1","0"]
]

Output: 6
```

## Intuition

Treat each row as the base of a histogram. Heights accumulate consecutive `1`s above the row, then use Largest Rectangle in Histogram.

## Solution

```python
def maximal_rectangle(matrix):
    if not matrix:
        return 0

    cols = len(matrix[0])
    heights = [0] * cols

    def largest_histogram_area():
        stack = []
        best = 0
        extended = heights + [0]

        for i, height in enumerate(extended):
            while stack and extended[stack[-1]] > height:
                h = extended[stack.pop()]
                left_boundary = stack[-1] if stack else -1
                width = i - left_boundary - 1
                best = max(best, h * width)
            stack.append(i)

        return best

    answer = 0
    for row in matrix:
        for c in range(cols):
            if row[c] == "1":
                heights[c] += 1
            else:
                heights[c] = 0

        answer = max(answer, largest_histogram_area())

    return answer
```

## Complexity

- Time: `O(rows * cols)`
- Space: `O(cols)`

