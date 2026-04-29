# Contains Duplicate

## Problem

Given an integer array `nums`, return `True` if any value appears at least twice.

## Input

- `nums`: list of integers

## Output

- Boolean

## Example

```text
Input: nums = [1, 2, 3, 1]
Output: True
```

## Intuition

While scanning, a hash set tells us whether we have already seen the current number.

## Solution

```python
def contains_duplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

