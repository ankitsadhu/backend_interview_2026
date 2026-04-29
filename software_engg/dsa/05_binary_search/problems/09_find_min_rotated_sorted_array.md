# Find Minimum in Rotated Sorted Array

## Problem

Given a rotated sorted array with distinct values, return the minimum element.

## Input

- `nums`: rotated sorted list of distinct integers

## Output

- Minimum value

## Example

```text
Input: nums = [3,4,5,1,2]
Output: 1
```

## Intuition

Compare `nums[mid]` with `nums[right]`. If mid is greater, the minimum is to the right. Otherwise, it is at mid or to the left.

## Solution

```python
def find_min(nums):
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid

    return nums[left]
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

