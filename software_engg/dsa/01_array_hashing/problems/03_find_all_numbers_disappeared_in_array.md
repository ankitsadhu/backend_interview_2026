# Find All Numbers Disappeared in an Array

## Problem

Given an array `nums` of length `n` where each value is in `[1, n]`, return all numbers in `[1, n]` that do not appear in `nums`.

## Input

- `nums`: list of integers

## Output

- Missing numbers

## Example

```text
Input: nums = [4,3,2,7,8,2,3,1]
Output: [5,6]
```

## Intuition

Use each value as an index marker. Mark the index `value - 1` as seen by making it negative.

## Solution

```python
def find_disappeared_numbers(nums):
    for value in nums:
        index = abs(value) - 1
        nums[index] = -abs(nums[index])

    ans = []
    for i, value in enumerate(nums):
        if value > 0:
            ans.append(i + 1)
    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(1)` excluding output

