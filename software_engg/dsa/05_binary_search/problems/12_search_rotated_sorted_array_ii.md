# Search in Rotated Sorted Array II

## Problem

Given a rotated sorted array that may contain duplicates, return `True` if `target` exists.

## Input

- `nums`: rotated sorted list of integers
- `target`: integer

## Output

- Boolean

## Example

```text
Input: nums = [2,5,6,0,0,1,2], target = 0
Output: True
```

## Intuition

When duplicates make the sorted half unclear, shrink both boundaries. Otherwise, use normal rotated-array search.

## Solution

```python
def search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return True

        if nums[left] == nums[mid] == nums[right]:
            left += 1
            right -= 1
        elif nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return False
```

## Complexity

- Time: `O(log n)` average, `O(n)` worst case with many duplicates
- Space: `O(1)`

