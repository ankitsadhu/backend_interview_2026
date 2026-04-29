# Longest Valid Parentheses

## Problem

Given a string containing only `(` and `)`, return the length of the longest valid parentheses substring.

## Input

- `s`: parentheses string

## Output

- Maximum valid length

## Example

```text
Input: s = ")()())"
Output: 4
```

## Intuition

Use a stack of indices. Keep a base index for the last unmatched closing parenthesis.

## Solution

```python
def longest_valid_parentheses(s):
    stack = [-1]
    best = 0

    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                best = max(best, i - stack[-1])

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

