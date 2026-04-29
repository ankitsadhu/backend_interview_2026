# Letter Case Permutation

## Problem

Given a string `s`, return all strings formed by changing each letter independently to lowercase or uppercase. Digits remain unchanged.

## Input

- `s`: alphanumeric string

## Output

- List of all case permutations

## Example

```text
Input: s = "a1b2"
Output: ["a1b2", "a1B2", "A1b2", "A1B2"]
```

## Intuition

For letters, branch into lowercase and uppercase. For digits, move ahead with only one choice.

## Solution

```python
def letter_case_permutation(s):
    ans = []

    def backtrack(i, path):
        if i == len(s):
            ans.append("".join(path))
            return

        ch = s[i]
        if ch.isalpha():
            path.append(ch.lower())
            backtrack(i + 1, path)
            path.pop()

            path.append(ch.upper())
            backtrack(i + 1, path)
            path.pop()
        else:
            path.append(ch)
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return ans
```

## Complexity

- Time: `O(2^L * n)`, where `L` is the number of letters
- Space: `O(n)` recursion stack, excluding output

