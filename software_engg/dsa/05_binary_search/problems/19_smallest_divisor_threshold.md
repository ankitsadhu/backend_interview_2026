# Find the Smallest Divisor Given a Threshold

## Problem

Given `nums` and `threshold`, choose the smallest positive divisor such that the sum of `ceil(num / divisor)` for all numbers is at most `threshold`.

## Input

- `nums`: list of positive integers
- `threshold`: maximum allowed sum

## Output

- Smallest feasible divisor

## Example

```text
Input: nums = [1,2,5,9], threshold = 6
Output: 5
```

## Intuition

A larger divisor makes the sum smaller. Binary search the smallest divisor that satisfies the threshold.

## Solution

```python
def smallest_divisor(nums, threshold):
    left, right = 1, max(nums)

    def can(divisor):
        total = 0
        for num in nums:
            total += (num + divisor - 1) // divisor
        return total <= threshold

    while left < right:
        mid = left + (right - left) // 2
        if can(mid):
            right = mid
        else:
            left = mid + 1

    return left
```

## Complexity

- Time: `O(n log max(nums))`
- Space: `O(1)`

