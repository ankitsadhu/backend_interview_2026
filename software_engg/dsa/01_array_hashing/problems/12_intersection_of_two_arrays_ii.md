# Intersection of Two Arrays II

## Problem

Given two arrays, return their intersection including duplicate counts.

## Input

- `nums1`: list of integers
- `nums2`: list of integers

## Output

- Common values with multiplicity

## Example

```text
Input: nums1 = [1,2,2,1], nums2 = [2,2]
Output: [2,2]
```

## Intuition

Count values from the smaller array, then consume counts while scanning the other.

## Solution

```python
from collections import Counter

def intersect(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    count = Counter(nums1)
    ans = []

    for num in nums2:
        if count[num] > 0:
            ans.append(num)
            count[num] -= 1

    return ans
```

## Complexity

- Time: `O(n + m)`
- Space: `O(min(n, m))`

