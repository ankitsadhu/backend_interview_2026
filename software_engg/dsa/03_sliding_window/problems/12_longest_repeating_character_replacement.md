# Longest Repeating Character Replacement

## Problem

Given a string `s` and integer `k`, return the length of the longest substring that can be changed into all the same character by replacing at most `k` characters.

## Input

- `s`: uppercase string
- `k`: maximum replacements

## Output

- Maximum length

## Example

```text
Input: s = "AABABBA", k = 1
Output: 4
```

## Intuition

For a window, replacements needed are `window_length - max_frequency_in_window`. Keep this value at most `k`.

## Solution

```python
from collections import defaultdict

def character_replacement(s, k):
    count = defaultdict(int)
    left = 0
    max_freq = 0
    best = 0

    for right, ch in enumerate(s):
        count[ch] += 1
        max_freq = max(max_freq, count[ch])

        while (right - left + 1) - max_freq > k:
            count[s[left]] -= 1
            left += 1

        best = max(best, right - left + 1)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)` for uppercase English letters

