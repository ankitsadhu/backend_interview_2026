# Maximum Length of a Concatenated String with Unique Characters

## Problem

Given an array of strings `arr`, choose a subsequence and concatenate it so that all characters in the result are unique. Return the maximum possible length.

## Input

- `arr`: list of lowercase strings

## Output

- Maximum length of a concatenation with unique characters

## Example

```text
Input: arr = ["un", "iq", "ue"]
Output: 4
```

## Intuition

Convert each valid word to a bitmask. Then use subset recursion: skip the word, or take it only if its mask does not overlap with the current mask.

## Solution

```python
def max_length(arr):
    masks = []

    for word in arr:
        mask = 0
        valid = True
        for ch in word:
            bit = 1 << (ord(ch) - ord("a"))
            if mask & bit:
                valid = False
                break
            mask |= bit
        if valid:
            masks.append((mask, len(word)))

    def backtrack(i, used_mask):
        if i == len(masks):
            return 0

        best = backtrack(i + 1, used_mask)
        word_mask, word_len = masks[i]
        if used_mask & word_mask == 0:
            best = max(best, word_len + backtrack(i + 1, used_mask | word_mask))
        return best

    return backtrack(0, 0)
```

## Complexity

- Time: `O(2^n)`
- Space: `O(n)` recursion stack

