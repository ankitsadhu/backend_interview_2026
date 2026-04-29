# Backspace String Compare

## Problem

Given strings `s` and `t`, return `True` if they are equal after applying backspaces. A `#` means delete the previous character.

## Input

- `s`: string
- `t`: string

## Output

- Boolean

## Example

```text
Input: s = "ab#c", t = "ad#c"
Output: True
```

## Intuition

Use a stack to simulate typing. Normal characters are pushed, and `#` pops when possible.

## Solution

```python
def backspace_compare(s, t):
    def build(text):
        stack = []
        for ch in text:
            if ch == "#":
                if stack:
                    stack.pop()
            else:
                stack.append(ch)
        return stack

    return build(s) == build(t)
```

## Complexity

- Time: `O(n + m)`
- Space: `O(n + m)`

