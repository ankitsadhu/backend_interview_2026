# Longest Substring with At Most Two Distinct Characters

## Problem

Given a string `s`, return the length of the longest substring that contains at most two distinct characters.

## Input

- `s`: string

## Output

- Maximum length

## Example

```text
Input: s = "eceba"
Output: 3
```

## Intuition

Use a frequency map for characters in the current window. Shrink when distinct count becomes greater than two.

## Solution

```python
from collections import defaultdict

def length_of_longest_substring_two_distinct(s):
    count = defaultdict(int)
    left = 0
    best = 0

    for right, ch in enumerate(s):
        count[ch] += 1

        while len(count) > 2:
            count[s[left]] -= 1
            if count[s[left]] == 0:
                del count[s[left]]
            left += 1

        best = max(best, right - left + 1)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)` because the window tracks at most three characters before shrinking

