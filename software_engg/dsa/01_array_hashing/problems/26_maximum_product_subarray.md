# Maximum Product Subarray

## Problem

Given an integer array `nums`, return the maximum product of a contiguous subarray.

## Input

- `nums`: list of integers

## Output

- Maximum product

## Example

```text
Input: nums = [2,3,-2,4]
Output: 6
```

## Intuition

A negative number can turn the smallest product into the largest. Track both max and min products ending here.

## Solution

```python
def max_product(nums):
    current_max = current_min = best = nums[0]

    for num in nums[1:]:
        if num < 0:
            current_max, current_min = current_min, current_max

        current_max = max(num, current_max * num)
        current_min = min(num, current_min * num)
        best = max(best, current_max)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

