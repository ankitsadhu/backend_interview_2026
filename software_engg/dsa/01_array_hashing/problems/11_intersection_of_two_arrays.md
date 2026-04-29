# Intersection of Two Arrays

## Problem

Given two arrays, return their unique intersection.

## Input

- `nums1`: list of integers
- `nums2`: list of integers

## Output

- Unique values present in both arrays

## Example

```text
Input: nums1 = [1,2,2,1], nums2 = [2,2]
Output: [2]
```

## Intuition

Convert both arrays to sets and intersect them.

## Solution

```python
def intersection(nums1, nums2):
    return list(set(nums1) & set(nums2))
```

## Complexity

- Time: `O(n + m)`
- Space: `O(n + m)`

