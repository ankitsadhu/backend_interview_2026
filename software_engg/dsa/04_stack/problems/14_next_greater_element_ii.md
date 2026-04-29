# Next Greater Element II

## Problem

Given a circular array `nums`, return the next greater number for every element.

## Input

- `nums`: list of integers

## Output

- List of next greater values, or `-1`

## Example

```text
Input: nums = [1,2,1]
Output: [2,-1,2]
```

## Intuition

Loop through the array twice. Store indices in a decreasing stack so circular next-greater values can resolve during the second pass.

## Solution

```python
def next_greater_elements(nums):
    n = len(nums)
    ans = [-1] * n
    stack = []

    for i in range(2 * n):
        index = i % n
        while stack and nums[stack[-1]] < nums[index]:
            ans[stack.pop()] = nums[index]
        if i < n:
            stack.append(index)

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

