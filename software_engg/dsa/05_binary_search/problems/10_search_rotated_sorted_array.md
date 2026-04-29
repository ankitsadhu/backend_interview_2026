# Search in Rotated Sorted Array

## Problem

Given a rotated sorted array with distinct values, return the index of `target`, or `-1`.

## Input

- `nums`: rotated sorted list of distinct integers
- `target`: integer

## Output

- Index of `target` or `-1`

## Example

```text
Input: nums = [4,5,6,7,0,1,2], target = 0
Output: 4
```

## Intuition

At least one half is sorted. Decide whether target lies in the sorted half, then discard the other half.

## Solution

```python
def search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid

        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

