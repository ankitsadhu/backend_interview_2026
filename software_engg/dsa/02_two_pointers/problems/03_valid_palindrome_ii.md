# Valid Palindrome II

## Problem

Given a string `s`, return `True` if it can become a palindrome after deleting at most one character.

## Input

- `s`: string

## Output

- Boolean

## Example

```text
Input: s = "abca"
Output: True
```

## Intuition

When the first mismatch appears, the only possible fixes are skipping the left character or skipping the right character.

## Solution

```python
def valid_palindrome(s):
    def check(left, right):
        while left < right:
            if s[left] != s[right]:
                return False
            left += 1
            right -= 1
        return True

    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return check(left + 1, right) or check(left, right - 1)
        left += 1
        right -= 1

    return True
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

