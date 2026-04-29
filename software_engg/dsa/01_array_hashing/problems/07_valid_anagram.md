# Valid Anagram

## Problem

Given strings `s` and `t`, return `True` if `t` is an anagram of `s`.

## Input

- `s`: string
- `t`: string

## Output

- Boolean

## Example

```text
Input: s = "anagram", t = "nagaram"
Output: True
```

## Intuition

Two anagrams have the same character frequencies.

## Solution

```python
from collections import Counter

def is_anagram(s, t):
    return Counter(s) == Counter(t)
```

## Complexity

- Time: `O(n + m)`
- Space: `O(1)` for lowercase English letters, otherwise `O(n + m)`

