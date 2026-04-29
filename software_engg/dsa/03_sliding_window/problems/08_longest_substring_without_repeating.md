# Longest Substring Without Repeating Characters

## Problem

Given a string `s`, return the length of the longest substring without repeating characters.

## Input

- `s`: string

## Output

- Maximum length

## Example

```text
Input: s = "abcabcbb"
Output: 3
```

## Intuition

Keep a window with unique characters. If a duplicate enters, remove characters from the left until the duplicate is gone.

## Solution

```python
def length_of_longest_substring(s):
    seen = set()
    left = 0
    best = 0

    for right, ch in enumerate(s):
        while ch in seen:
            seen.remove(s[left])
            left += 1

        seen.add(ch)
        best = max(best, right - left + 1)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(min(n, charset))`

