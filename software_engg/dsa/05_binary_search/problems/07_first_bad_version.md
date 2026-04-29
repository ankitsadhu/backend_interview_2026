# First Bad Version

## Problem

Given versions `1` to `n` and an API `isBadVersion(version)`, return the first bad version.

## Input

- `n`: latest version
- `isBadVersion`: boolean API

## Output

- First bad version

## Example

```text
Input: n = 5, bad = 4
Output: 4
```

## Intuition

The search space is boolean: good versions first, then bad versions. Find the first `True`.

## Solution

```python
def first_bad_version(n):
    left, right = 1, n

    while left < right:
        mid = left + (right - left) // 2
        if isBadVersion(mid):
            right = mid
        else:
            left = mid + 1

    return left
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

