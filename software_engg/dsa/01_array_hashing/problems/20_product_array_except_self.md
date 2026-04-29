# Product of Array Except Self

## Problem

Given `nums`, return an array where each position contains the product of all other elements. Do not use division.

## Input

- `nums`: list of integers

## Output

- Product array

## Example

```text
Input: nums = [1,2,3,4]
Output: [24,12,8,6]
```

## Intuition

Each answer is product of everything to the left times everything to the right.

## Solution

```python
def product_except_self(nums):
    n = len(nums)
    ans = [1] * n

    prefix = 1
    for i in range(n):
        ans[i] = prefix
        prefix *= nums[i]

    suffix = 1
    for i in range(n - 1, -1, -1):
        ans[i] *= suffix
        suffix *= nums[i]

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(1)` excluding output

