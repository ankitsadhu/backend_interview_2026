# Palindrome Partitioning

## Problem

Given a string `s`, partition it so every substring in the partition is a palindrome. Return all possible palindrome partitions.

## Input

- `s`: string

## Output

- List of palindrome partitions

## Example

```text
Input: s = "aab"
Output: [["a", "a", "b"], ["aa", "b"]]
```

## Intuition

At each index, try every possible next cut. Continue only when the selected substring is a palindrome.

## Solution

```python
def partition(s):
    ans = []

    def is_palindrome(left, right):
        while left < right:
            if s[left] != s[right]:
                return False
            left += 1
            right -= 1
        return True

    def backtrack(start, path):
        if start == len(s):
            ans.append(path[:])
            return

        for end in range(start, len(s)):
            if not is_palindrome(start, end):
                continue

            path.append(s[start:end + 1])
            backtrack(end + 1, path)
            path.pop()

    backtrack(0, [])
    return ans
```

## Complexity

- Time: `O(2^n * n)`
- Space: `O(n)` recursion stack, excluding output

