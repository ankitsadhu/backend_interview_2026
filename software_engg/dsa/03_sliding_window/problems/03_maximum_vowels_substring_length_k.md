# Maximum Number of Vowels in a Substring of Given Length

## Problem

Given a string `s` and integer `k`, return the maximum number of vowel letters in any substring of length `k`.

## Input

- `s`: string
- `k`: window size

## Output

- Maximum vowel count

## Example

```text
Input: s = "abciiidef", k = 3
Output: 3
```

## Intuition

Track how many vowels are inside the current fixed-size window.

## Solution

```python
def max_vowels(s, k):
    vowels = set("aeiou")
    count = sum(1 for ch in s[:k] if ch in vowels)
    best = count

    for right in range(k, len(s)):
        if s[right] in vowels:
            count += 1
        if s[right - k] in vowels:
            count -= 1
        best = max(best, count)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

