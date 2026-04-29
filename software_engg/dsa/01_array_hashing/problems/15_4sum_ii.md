# 4Sum II

## Problem

Given four integer arrays `nums1`, `nums2`, `nums3`, and `nums4`, return the number of tuples `(i, j, k, l)` such that their values sum to `0`.

## Input

- `nums1`, `nums2`, `nums3`, `nums4`: integer arrays

## Output

- Count of zero-sum tuples

## Example

```text
Input: nums1 = [1,2], nums2 = [-2,-1], nums3 = [-1,2], nums4 = [0,2]
Output: 2
```

## Intuition

Store all pair sums from the first two arrays. For each pair sum from the last two arrays, look for its negation.

## Solution

```python
from collections import Counter

def four_sum_count(nums1, nums2, nums3, nums4):
    pair_count = Counter()
    for a in nums1:
        for b in nums2:
            pair_count[a + b] += 1

    ans = 0
    for c in nums3:
        for d in nums4:
            ans += pair_count[-(c + d)]

    return ans
```

## Complexity

- Time: `O(n^2)`
- Space: `O(n^2)`

