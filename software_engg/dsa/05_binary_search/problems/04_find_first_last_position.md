# Find First and Last Position of Element in Sorted Array

## Problem

Given a sorted array `nums` and a `target`, return the first and last index of `target`. Return `[-1, -1]` if not found.

## Input

- `nums`: sorted list of integers
- `target`: integer

## Output

- `[first_index, last_index]`

## Example

```text
Input: nums = [5,7,7,8,8,10], target = 8
Output: [3,4]
```

## Intuition

The first index is lower bound of target. The last index is upper bound of target minus one.

## Solution

```python
def search_range(nums, target):
    def lower_bound(x):
        left, right = 0, len(nums)
        while left < right:
            mid = left + (right - left) // 2
            if nums[mid] < x:
                left = mid + 1
            else:
                right = mid
        return left

    first = lower_bound(target)
    if first == len(nums) or nums[first] != target:
        return [-1, -1]

    last = lower_bound(target + 1) - 1
    return [first, last]
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

