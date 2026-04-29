# Merge Strings Alternately

## Problem

Given two strings `word1` and `word2`, merge them by alternating characters. Append the remaining suffix of the longer string.

## Input

- `word1`: string
- `word2`: string

## Output

- Merged string

## Example

```text
Input: word1 = "abc", word2 = "pqr"
Output: "apbqcr"
```

## Intuition

Use one pointer for each string and append from each side when available.

## Solution

```python
def merge_alternately(word1, word2):
    ans = []
    i = j = 0

    while i < len(word1) or j < len(word2):
        if i < len(word1):
            ans.append(word1[i])
            i += 1
        if j < len(word2):
            ans.append(word2[j])
            j += 1

    return "".join(ans)
```

## Complexity

- Time: `O(n + m)`
- Space: `O(n + m)`

