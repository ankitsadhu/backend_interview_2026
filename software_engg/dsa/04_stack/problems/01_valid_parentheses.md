# Valid Parentheses

## Problem

Given a string containing only parentheses characters, return `True` if every opening bracket is closed by the same type in the correct order.

## Input

- `s`: string containing `()[]{}` characters

## Output

- Boolean

## Example

```text
Input: s = "()[]{}"
Output: True
```

## Intuition

When we see a closing bracket, it must match the most recent unmatched opening bracket.

## Solution

```python
def is_valid(s):
    stack = []
    match = {")": "(", "]": "[", "}": "{"}

    for ch in s:
        if ch in match:
            if not stack or stack[-1] != match[ch]:
                return False
            stack.pop()
        else:
            stack.append(ch)

    return not stack
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

