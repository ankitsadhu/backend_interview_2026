# Longest Substring with At Most K Distinct Characters

## Problem

Given a string `s` and integer `k`, return the length of the longest substring that contains at most `k` distinct characters.

## Input

- `s`: string
- `k`: maximum distinct characters

## Output

- Maximum length

## Example

```text
Input: s = "eceba", k = 2
Output: 3
```

## Intuition

This generalizes the at-most-two-distinct pattern. Keep shrinking while the window has too many distinct characters.

## Solution

```python
from collections import defaultdict

def length_of_longest_substring_k_distinct(s, k):
    if k == 0:
        return 0

    count = defaultdict(int)
    left = 0
    best = 0

    for right, ch in enumerate(s):
        count[ch] += 1

        while len(count) > k:
            count[s[left]] -= 1
            if count[s[left]] == 0:
                del count[s[left]]
            left += 1

        best = max(best, right - left + 1)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(k)`

