# Single Element in a Sorted Array

## Problem

Given a sorted array where every element appears exactly twice except one element that appears once, return the single element.

## Input

- `nums`: sorted list of integers

## Output

- Single element

## Example

```text
Input: nums = [1,1,2,3,3,4,4,8,8]
Output: 2
```

## Intuition

Before the single element, pairs start at even indices. After it, pairs start at odd indices.

## Solution

```python
def single_non_duplicate(nums):
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2
        if mid % 2 == 1:
            mid -= 1

        if nums[mid] == nums[mid + 1]:
            left = mid + 2
        else:
            right = mid

    return nums[left]
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

