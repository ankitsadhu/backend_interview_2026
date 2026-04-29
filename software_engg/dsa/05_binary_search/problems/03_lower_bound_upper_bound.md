# Lower Bound and Upper Bound

## Problem

Given a sorted array `nums` and a `target`, implement:

- lower bound: first index where `nums[i] >= target`
- upper bound: first index where `nums[i] > target`

## Input

- `nums`: sorted list of integers
- `target`: integer

## Output

- Lower-bound and upper-bound indices

## Example

```text
Input: nums = [1,2,2,2,4], target = 2
Output: lower_bound = 1, upper_bound = 4
```

## Intuition

Use a half-open range `[left, right)`. The answer is the first index that satisfies the boundary condition.

## Solution

```python
def lower_bound(nums, target):
    left, right = 0, len(nums)

    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid

    return left

def upper_bound(nums, target):
    left, right = 0, len(nums)

    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] <= target:
            left = mid + 1
        else:
            right = mid

    return left
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

