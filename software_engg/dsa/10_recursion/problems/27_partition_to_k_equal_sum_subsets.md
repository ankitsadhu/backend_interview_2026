# Partition to K Equal Sum Subsets

## Problem

Given an integer array `nums` and an integer `k`, return `True` if the array can be partitioned into `k` non-empty subsets with equal sum.

## Input

- `nums`: list of positive integers
- `k`: number of subsets

## Output

- Boolean

## Example

```text
Input: nums = [4,3,2,3,5,2,1], k = 4
Output: True
Explanation: [5], [1,4], [2,3], [2,3]
```

## Intuition

The target sum for each bucket is `sum(nums) / k`. Put each number into one bucket at a time. Sorting descending helps fail faster.

## Solution

```python
def can_partition_k_subsets(nums, k):
    total = sum(nums)
    if total % k != 0:
        return False

    target = total // k
    nums.sort(reverse=True)
    if nums[0] > target:
        return False

    buckets = [0] * k

    def backtrack(i):
        if i == len(nums):
            return True

        value = nums[i]
        for bucket in range(k):
            if buckets[bucket] + value <= target:
                buckets[bucket] += value
                if backtrack(i + 1):
                    return True
                buckets[bucket] -= value

            if buckets[bucket] == 0:
                break

        return False

    return backtrack(0)
```

## Complexity

- Time: `O(k^n)` worst case
- Space: `O(k + n)`

