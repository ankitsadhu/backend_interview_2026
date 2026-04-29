# Find All Anagrams in a String

## Problem

Given strings `s` and `p`, return all start indices of `p`'s anagrams in `s`.

## Input

- `s`: source string
- `p`: pattern string

## Output

- List of start indices

## Example

```text
Input: s = "cbaebabacd", p = "abc"
Output: [0, 6]
```

## Intuition

Use a fixed-size frequency window of length `len(p)`.

## Solution

```python
from collections import Counter

def find_anagrams(s, p):
    need = Counter(p)
    window = Counter()
    k = len(p)
    ans = []

    for right, ch in enumerate(s):
        window[ch] += 1

        if right >= k:
            left_ch = s[right - k]
            window[left_ch] -= 1
            if window[left_ch] == 0:
                del window[left_ch]

        if window == need:
            ans.append(right - k + 1)

    return ans
```

## Complexity

- Time: `O(n)` for fixed lowercase alphabet
- Space: `O(1)` for fixed lowercase alphabet

