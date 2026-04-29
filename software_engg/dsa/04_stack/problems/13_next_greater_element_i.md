# Next Greater Element I

## Problem

Given arrays `nums1` and `nums2`, where `nums1` is a subset of `nums2`, return the next greater element in `nums2` for each value in `nums1`.

## Input

- `nums1`: query values
- `nums2`: source values

## Output

- Next greater value for each query, or `-1`

## Example

```text
Input: nums1 = [4,1,2], nums2 = [1,3,4,2]
Output: [-1,3,-1]
```

## Intuition

Use a decreasing stack. When a larger value appears, it is the next greater value for smaller values waiting on the stack.

## Solution

```python
def next_greater_element(nums1, nums2):
    next_greater = {}
    stack = []

    for num in nums2:
        while stack and stack[-1] < num:
            next_greater[stack.pop()] = num
        stack.append(num)

    return [next_greater.get(num, -1) for num in nums1]
```

## Complexity

- Time: `O(n + m)`
- Space: `O(n)`

