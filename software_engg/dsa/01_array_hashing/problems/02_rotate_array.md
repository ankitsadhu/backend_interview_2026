# Rotate Array

## Problem

Given an array `nums`, rotate it to the right by `k` steps in-place.

## Input

- `nums`: list of integers
- `k`: number of rotations

## Output

- Modify `nums` in-place

## Example

```text
Input: nums = [1,2,3,4,5,6,7], k = 3
Output: [5,6,7,1,2,3,4]
```

## Intuition

Reverse the whole array, then reverse the first `k` elements and the remaining elements.

## Solution

```python
def rotate(nums, k):
    n = len(nums)
    k %= n

    def reverse(left, right):
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1

    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

