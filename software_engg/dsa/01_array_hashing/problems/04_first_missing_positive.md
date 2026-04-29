# First Missing Positive

## Problem

Given an unsorted integer array, return the smallest missing positive integer. Use `O(n)` time and `O(1)` extra space.

## Input

- `nums`: list of integers

## Output

- Smallest missing positive integer

## Example

```text
Input: nums = [3, 4, -1, 1]
Output: 2
```

## Intuition

Place each value `x` in index `x - 1` if `1 <= x <= n`. Then the first wrong index reveals the answer.

## Solution

```python
def first_missing_positive(nums):
    n = len(nums)

    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            correct = nums[i] - 1
            nums[i], nums[correct] = nums[correct], nums[i]

    for i, value in enumerate(nums):
        if value != i + 1:
            return i + 1

    return n + 1
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

