# Substring with Concatenation of All Words

## Problem

Given a string `s` and a list of equal-length words, return all starting indices where a substring is the concatenation of each word exactly once.

## Input

- `s`: source string
- `words`: list of words with equal length

## Output

- List of start indices

## Example

```text
Input: s = "barfoothefoobarman", words = ["foo", "bar"]
Output: [0, 9]
```

## Intuition

Because all words have the same length, scan in word-sized steps for each possible offset. Keep a frequency window of words.

## Solution

```python
from collections import Counter, defaultdict

def find_substring(s, words):
    if not s or not words:
        return []

    word_len = len(words[0])
    word_count = len(words)
    total_len = word_len * word_count
    need = Counter(words)
    ans = []

    for offset in range(word_len):
        left = offset
        seen = defaultdict(int)
        used = 0

        for right in range(offset, len(s) - word_len + 1, word_len):
            word = s[right:right + word_len]

            if word not in need:
                seen.clear()
                used = 0
                left = right + word_len
                continue

            seen[word] += 1
            used += 1

            while seen[word] > need[word]:
                left_word = s[left:left + word_len]
                seen[left_word] -= 1
                used -= 1
                left += word_len

            if used == word_count:
                ans.append(left)
                left_word = s[left:left + word_len]
                seen[left_word] -= 1
                used -= 1
                left += word_len

    return ans
```

## Complexity

- Time: `O(n * word_length)`
- Space: `O(number of words)`

