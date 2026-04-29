# Find Peak Element

## Problem

Given an array `nums`, find a peak element and return its index. A peak is greater than its neighbors.

## Input

- `nums`: list of integers

## Output

- Index of a peak element

## Example

```text
Input: nums = [1,2,3,1]
Output: 2
```

## Intuition

If `nums[mid] < nums[mid + 1]`, a peak must exist to the right. Otherwise, a peak exists at mid or to the left.

## Solution

```python
def find_peak_element(nums):
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < nums[mid + 1]:
            left = mid + 1
        else:
            right = mid

    return left
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

