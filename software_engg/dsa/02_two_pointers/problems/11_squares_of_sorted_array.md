# Squares of a Sorted Array

## Problem

Given a sorted integer array `nums`, return an array of the squares of each number, also sorted.

## Input

- `nums`: sorted list of integers

## Output

- Sorted squares

## Example

```text
Input: nums = [-4,-1,0,3,10]
Output: [0,1,9,16,100]
```

## Intuition

The largest square is at one of the two ends. Fill the answer from right to left.

## Solution

```python
def sorted_squares(nums):
    left, right = 0, len(nums) - 1
    ans = [0] * len(nums)
    write = len(nums) - 1

    while left <= right:
        if abs(nums[left]) > abs(nums[right]):
            ans[write] = nums[left] * nums[left]
            left += 1
        else:
            ans[write] = nums[right] * nums[right]
            right -= 1
        write -= 1

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

