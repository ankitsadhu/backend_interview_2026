# Binary Search

## Problem

Given a sorted array `nums` and a `target`, return the index of `target` or `-1` if it does not exist.

## Input

- `nums`: sorted list of integers
- `target`: integer

## Output

- Index of `target` or `-1`

## Example

```text
Input: nums = [-1,0,3,5,9,12], target = 9
Output: 4
```

## Intuition

Compare the target with the middle element. Discard the half where the target cannot exist.

## Solution

```python
def search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

