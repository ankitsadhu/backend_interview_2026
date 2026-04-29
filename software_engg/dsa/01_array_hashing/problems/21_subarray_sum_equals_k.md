# Subarray Sum Equals K

## Problem

Given an integer array `nums` and integer `k`, return the total number of continuous subarrays whose sum equals `k`.

## Input

- `nums`: list of integers
- `k`: target sum

## Output

- Count of subarrays

## Example

```text
Input: nums = [1,1,1], k = 2
Output: 2
```

## Intuition

If current prefix sum is `prefix`, then a previous prefix of `prefix - k` forms a subarray sum of `k`.

## Solution

```python
from collections import defaultdict

def subarray_sum(nums, k):
    freq = defaultdict(int)
    freq[0] = 1
    prefix = 0
    ans = 0

    for num in nums:
        prefix += num
        ans += freq[prefix - k]
        freq[prefix] += 1

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

