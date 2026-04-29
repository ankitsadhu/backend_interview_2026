# Running Sum of 1D Array

## Problem

Given `nums`, return an array where `ans[i]` is the sum of `nums[0]` through `nums[i]`.

## Input

- `nums`: list of integers

## Output

- Running sum array

## Example

```text
Input: nums = [1, 2, 3, 4]
Output: [1, 3, 6, 10]
```

## Intuition

Keep a running total while scanning left to right.

## Solution

```python
def running_sum(nums):
    total = 0
    ans = []
    for num in nums:
        total += num
        ans.append(total)
    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(n)` for output

