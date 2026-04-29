# Maximum Subarray

## Problem

Given an integer array `nums`, find the contiguous subarray with the largest sum and return its sum.

## Input

- `nums`: list of integers

## Output

- Maximum subarray sum

## Example

```text
Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6
```

## Intuition

At each index, decide whether to extend the previous subarray or start fresh.

## Solution

```python
def max_sub_array(nums):
    current = best = nums[0]

    for num in nums[1:]:
        current = max(num, current + num)
        best = max(best, current)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

