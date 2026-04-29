# Search Insert Position

## Problem

Given a sorted array `nums` and a `target`, return the index if found. Otherwise, return the index where it should be inserted.

## Input

- `nums`: sorted list of distinct integers
- `target`: integer

## Output

- Existing or insertion index

## Example

```text
Input: nums = [1,3,5,6], target = 5
Output: 2
```

## Intuition

This is lower bound: find the first index where `nums[i] >= target`.

## Solution

```python
def search_insert(nums, target):
    left, right = 0, len(nums)

    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid

    return left
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

