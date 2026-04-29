# Find Minimum in Rotated Sorted Array II

## Problem

Given a rotated sorted array that may contain duplicates, return the minimum element.

## Input

- `nums`: rotated sorted list of integers

## Output

- Minimum value

## Example

```text
Input: nums = [2,2,2,0,1]
Output: 0
```

## Intuition

Duplicates can hide which half contains the minimum. When `nums[mid] == nums[right]`, safely shrink `right` by one.

## Solution

```python
def find_min(nums):
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2

        if nums[mid] > nums[right]:
            left = mid + 1
        elif nums[mid] < nums[right]:
            right = mid
        else:
            right -= 1

    return nums[left]
```

## Complexity

- Time: `O(log n)` average, `O(n)` worst case with many duplicates
- Space: `O(1)`

