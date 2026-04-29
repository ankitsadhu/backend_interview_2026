# Simplify Path

## Problem

Given an absolute Unix path, return its simplified canonical path.

## Input

- `path`: absolute path string

## Output

- Simplified path

## Example

```text
Input: path = "/home//foo/"
Output: "/home/foo"
```

## Intuition

Path components behave like a stack. Normal names push, `".."` pops, and `"."` or empty parts are ignored.

## Solution

```python
def simplify_path(path):
    stack = []

    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)

    return "/" + "/".join(stack)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

