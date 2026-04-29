# Minimum Size Subarray Sum

## Problem

Given an array of positive integers `nums` and integer `target`, return the minimum length of a contiguous subarray whose sum is at least `target`. Return `0` if none exists.

## Input

- `target`: required sum
- `nums`: list of positive integers

## Output

- Minimum valid length

## Example

```text
Input: target = 7, nums = [2,3,1,2,4,3]
Output: 2
```

## Intuition

Because numbers are positive, expanding right increases the sum and shrinking left decreases it.

## Solution

```python
def min_sub_array_len(target, nums):
    left = 0
    window_sum = 0
    best = float("inf")

    for right, value in enumerate(nums):
        window_sum += value

        while window_sum >= target:
            best = min(best, right - left + 1)
            window_sum -= nums[left]
            left += 1

    return 0 if best == float("inf") else best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

