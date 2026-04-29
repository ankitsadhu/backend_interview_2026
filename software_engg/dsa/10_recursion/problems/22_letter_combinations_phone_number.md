# Letter Combinations of a Phone Number

## Problem

Given a string containing digits from `2` to `9`, return all possible letter combinations the number could represent.

## Input

- `digits`: string of digits from `2` to `9`

## Output

- List of letter combinations

## Example

```text
Input: digits = "23"
Output: ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
```

## Intuition

Each digit gives a set of choices. Recursively choose one letter for the current digit.

## Solution

```python
def letter_combinations(digits):
    if not digits:
        return []

    mapping = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
    }
    ans = []

    def backtrack(i, path):
        if i == len(digits):
            ans.append("".join(path))
            return

        for ch in mapping[digits[i]]:
            path.append(ch)
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return ans
```

## Complexity

- Time: `O(4^n * n)` worst case
- Space: `O(n)` recursion stack, excluding output

