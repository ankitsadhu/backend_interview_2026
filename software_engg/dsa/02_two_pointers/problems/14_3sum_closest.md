# 3Sum Closest

## Problem

Given an integer array `nums` and integer `target`, return the sum of three integers closest to `target`.

## Input

- `nums`: list of integers
- `target`: integer

## Output

- Closest triplet sum

## Example

```text
Input: nums = [-1,2,1,-4], target = 1
Output: 2
```

## Intuition

Sort the array. For each fixed value, move two pointers based on whether the current sum is below or above target.

## Solution

```python
def three_sum_closest(nums, target):
    nums.sort()
    best = nums[0] + nums[1] + nums[2]

    for i in range(len(nums) - 2):
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]

            if abs(total - target) < abs(best - target):
                best = total
            if total < target:
                left += 1
            elif total > target:
                right -= 1
            else:
                return target

    return best
```

## Complexity

- Time: `O(n^2)`
- Space: `O(1)` excluding sort stack

