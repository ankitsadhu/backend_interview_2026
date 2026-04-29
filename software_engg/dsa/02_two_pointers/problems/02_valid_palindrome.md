# Valid Palindrome

## Problem

Given a string `s`, return `True` if it is a palindrome after converting uppercase letters to lowercase and removing non-alphanumeric characters.

## Input

- `s`: string

## Output

- Boolean

## Example

```text
Input: s = "A man, a plan, a canal: Panama"
Output: True
```

## Intuition

Move inward from both ends. Skip characters that should not participate in the comparison.

## Solution

```python
def is_palindrome(s):
    left, right = 0, len(s) - 1

    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1

        if s[left].lower() != s[right].lower():
            return False

        left += 1
        right -= 1

    return True
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

