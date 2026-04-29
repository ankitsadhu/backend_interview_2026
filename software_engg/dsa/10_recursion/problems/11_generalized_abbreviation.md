# Generalized Abbreviation

## Problem

Given a word, generate all generalized abbreviations. Consecutive abbreviated characters are represented by a count.

## Input

- `word`: string

## Output

- List of abbreviations

## Example

```text
Input: word = "word"
Output: ["word", "wor1", "wo1d", "wo2", "w1rd", ...]
```

## Intuition

For each character, either keep it or abbreviate it. Keep a running count of abbreviated characters and flush that count before adding a real character.

## Solution

```python
def generate_abbreviations(word):
    ans = []

    def backtrack(i, path, count):
        if i == len(word):
            if count:
                path.append(str(count))
            ans.append("".join(path))
            if count:
                path.pop()
            return

        backtrack(i + 1, path, count + 1)

        if count:
            path.append(str(count))
        path.append(word[i])
        backtrack(i + 1, path, 0)
        path.pop()
        if count:
            path.pop()

    backtrack(0, [], 0)
    return ans
```

## Complexity

- Time: `O(2^n * n)`
- Space: `O(n)` recursion stack, excluding output

