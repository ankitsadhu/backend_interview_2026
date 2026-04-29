# Generate Parentheses

## Problem

Given `n` pairs of parentheses, generate all valid combinations.

## Input

- `n`: number of pairs

## Output

- List of valid strings

## Example

```text
Input: n = 3
Output: ["((()))", "(()())", "(())()", "()(())", "()()()"]
```

## Intuition

A valid prefix can add `(` if open count is below `n`, and can add `)` only if it does not exceed open count.

## Solution

```python
def generate_parenthesis(n):
    ans = []

    def backtrack(path, open_count, close_count):
        if len(path) == 2 * n:
            ans.append("".join(path))
            return

        if open_count < n:
            path.append("(")
            backtrack(path, open_count + 1, close_count)
            path.pop()

        if close_count < open_count:
            path.append(")")
            backtrack(path, open_count, close_count + 1)
            path.pop()

    backtrack([], 0, 0)
    return ans
```

## Complexity

- Time: `O(Cn * n)`, where `Cn` is the `n`th Catalan number
- Space: `O(n)` recursion stack, excluding output

