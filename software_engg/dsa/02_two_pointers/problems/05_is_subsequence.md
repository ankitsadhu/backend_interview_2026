# Is Subsequence

## Problem

Given strings `s` and `t`, return `True` if `s` is a subsequence of `t`.

## Input

- `s`: target subsequence
- `t`: source string

## Output

- Boolean

## Example

```text
Input: s = "abc", t = "ahbgdc"
Output: True
```

## Intuition

Scan `t`. Move the pointer in `s` only when a needed character is matched.

## Solution

```python
def is_subsequence(s, t):
    i = 0

    for ch in t:
        if i < len(s) and s[i] == ch:
            i += 1

    return i == len(s)
```

## Complexity

- Time: `O(n + m)`
- Space: `O(1)`

