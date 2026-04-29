# Reverse String

## Problem

Given a list of characters `s`, reverse it in-place.

## Input

- `s`: list of characters

## Output

- Modify `s` in-place

## Example

```text
Input: s = ["h","e","l","l","o"]
Output: ["o","l","l","e","h"]
```

## Intuition

Swap the outer characters, then move both pointers inward.

## Solution

```python
def reverse_string(s):
    left, right = 0, len(s) - 1

    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

