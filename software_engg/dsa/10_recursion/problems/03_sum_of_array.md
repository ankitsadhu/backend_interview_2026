# Sum of Array

## Problem

Given an array of integers, return the sum of all elements using recursion.

## Input

- `nums`: list of integers

## Output

- Sum of all elements

## Example

```text
Input: nums = [2, 4, 6]
Output: 12
```

## Intuition

At index `i`, add `nums[i]` to the sum of the remaining suffix.

## Solution

```python
def array_sum(nums):
    def dfs(i):
        if i == len(nums):
            return 0
        return nums[i] + dfs(i + 1)

    return dfs(0)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

