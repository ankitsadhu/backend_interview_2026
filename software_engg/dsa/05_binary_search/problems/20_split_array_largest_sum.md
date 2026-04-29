# Split Array Largest Sum

## Problem

Given an array `nums` and integer `k`, split `nums` into `k` non-empty continuous subarrays to minimize the largest subarray sum.

## Input

- `nums`: list of non-negative integers
- `k`: number of subarrays

## Output

- Minimum possible largest sum

## Example

```text
Input: nums = [7,2,5,10,8], k = 2
Output: 18
```

## Intuition

The answer lies between `max(nums)` and `sum(nums)`. Check if a maximum allowed sum can split the array into at most `k` parts.

## Solution

```python
def split_array(nums, k):
    left, right = max(nums), sum(nums)

    def can(max_sum):
        parts = 1
        current = 0

        for num in nums:
            if current + num > max_sum:
                parts += 1
                current = 0
            current += num

        return parts <= k

    while left < right:
        mid = left + (right - left) // 2
        if can(mid):
            right = mid
        else:
            left = mid + 1

    return left
```

## Complexity

- Time: `O(n log sum(nums))`
- Space: `O(1)`

