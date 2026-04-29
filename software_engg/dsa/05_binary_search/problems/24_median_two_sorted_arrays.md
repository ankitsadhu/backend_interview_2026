# Median of Two Sorted Arrays

## Problem

Given two sorted arrays `nums1` and `nums2`, return the median of the two sorted arrays in `O(log(m + n))` time.

## Input

- `nums1`: sorted list of integers
- `nums2`: sorted list of integers

## Output

- Median value

## Example

```text
Input: nums1 = [1,3], nums2 = [2]
Output: 2.0
```

## Intuition

Partition both arrays so the left half contains half the total elements and every left value is `<=` every right value. Binary search the partition in the smaller array.

## Solution

```python
def find_median_sorted_arrays(nums1, nums2):
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    total_left = (m + n + 1) // 2
    left, right = 0, m

    while left <= right:
        cut1 = left + (right - left) // 2
        cut2 = total_left - cut1

        left1 = float("-inf") if cut1 == 0 else nums1[cut1 - 1]
        right1 = float("inf") if cut1 == m else nums1[cut1]
        left2 = float("-inf") if cut2 == 0 else nums2[cut2 - 1]
        right2 = float("inf") if cut2 == n else nums2[cut2]

        if left1 <= right2 and left2 <= right1:
            if (m + n) % 2 == 1:
                return float(max(left1, left2))
            return (max(left1, left2) + min(right1, right2)) / 2

        if left1 > right2:
            right = cut1 - 1
        else:
            left = cut1 + 1
```

## Complexity

- Time: `O(log min(m, n))`
- Space: `O(1)`

