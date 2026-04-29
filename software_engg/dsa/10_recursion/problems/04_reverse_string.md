# Reverse String

## Problem

Given a list of characters, reverse it in-place using recursion.

## Input

- `s`: list of characters

## Output

- Same list modified in-place

## Example

```text
Input: s = ["h", "e", "l", "l", "o"]
Output: ["o", "l", "l", "e", "h"]
```

## Intuition

Swap the left and right characters, then recurse into the smaller middle section.

## Solution

```python
def reverse_string(s):
    def dfs(left, right):
        if left >= right:
            return

        s[left], s[right] = s[right], s[left]
        dfs(left + 1, right - 1)

    dfs(0, len(s) - 1)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

