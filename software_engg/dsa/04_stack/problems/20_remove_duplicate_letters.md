# Remove Duplicate Letters

## Problem

Given a string `s`, remove duplicate letters so every letter appears once and the result is lexicographically smallest among all possible results.

## Input

- `s`: lowercase string

## Output

- Lexicographically smallest unique-letter string

## Example

```text
Input: s = "cbacdcbc"
Output: "acdb"
```

## Intuition

Use a monotonic stack, but only pop a larger character if it appears again later.

## Solution

```python
def remove_duplicate_letters(s):
    last = {ch: i for i, ch in enumerate(s)}
    stack = []
    in_stack = set()

    for i, ch in enumerate(s):
        if ch in in_stack:
            continue

        while stack and stack[-1] > ch and last[stack[-1]] > i:
            in_stack.remove(stack.pop())

        stack.append(ch)
        in_stack.add(ch)

    return "".join(stack)
```

## Complexity

- Time: `O(n)`
- Space: `O(1)` for lowercase English letters

