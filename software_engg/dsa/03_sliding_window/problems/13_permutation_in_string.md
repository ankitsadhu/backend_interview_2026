# Permutation in String

## Problem

Given strings `s1` and `s2`, return `True` if `s2` contains a permutation of `s1`.

## Input

- `s1`: pattern string
- `s2`: source string

## Output

- Boolean

## Example

```text
Input: s1 = "ab", s2 = "eidbaooo"
Output: True
```

## Intuition

Every permutation of `s1` has the same character counts. Check every window of length `len(s1)` in `s2`.

## Solution

```python
from collections import Counter

def check_inclusion(s1, s2):
    need = Counter(s1)
    window = Counter()
    k = len(s1)

    for right, ch in enumerate(s2):
        window[ch] += 1

        if right >= k:
            left_ch = s2[right - k]
            window[left_ch] -= 1
            if window[left_ch] == 0:
                del window[left_ch]

        if window == need:
            return True

    return False
```

## Complexity

- Time: `O(n)` for fixed lowercase alphabet
- Space: `O(1)` for fixed lowercase alphabet

