# Minimum Window Substring

## Problem

Given strings `s` and `t`, return the minimum window substring of `s` that contains every character in `t`, including duplicates.

## Input

- `s`: source string
- `t`: required characters

## Output

- Minimum covering substring, or `""`

## Example

```text
Input: s = "ADOBECODEBANC", t = "ABC"
Output: "BANC"
```

## Intuition

Expand right until the window covers all required characters. Then shrink left while it remains valid to minimize it.

## Solution

```python
from collections import Counter, defaultdict

def min_window(s, t):
    if not t:
        return ""

    need = Counter(t)
    window = defaultdict(int)
    required = len(need)
    formed = 0
    left = 0
    best_len = float("inf")
    best_start = 0

    for right, ch in enumerate(s):
        window[ch] += 1
        if ch in need and window[ch] == need[ch]:
            formed += 1

        while formed == required:
            if right - left + 1 < best_len:
                best_len = right - left + 1
                best_start = left

            left_ch = s[left]
            window[left_ch] -= 1
            if left_ch in need and window[left_ch] < need[left_ch]:
                formed -= 1
            left += 1

    if best_len == float("inf"):
        return ""
    return s[best_start:best_start + best_len]
```

## Complexity

- Time: `O(n + m)`
- Space: `O(n + m)` for character maps

