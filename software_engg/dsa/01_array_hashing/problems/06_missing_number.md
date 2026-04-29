# Missing Number

## Problem

Given `nums` containing `n` distinct numbers from `0` to `n`, return the only number missing from the array.

## Input

- `nums`: list of distinct integers

## Output

- Missing number

## Example

```text
Input: nums = [3, 0, 1]
Output: 2
```

## Intuition

The expected sum from `0` to `n` minus the actual sum gives the missing value.

## Solution

```python
def missing_number(nums):
    n = len(nums)
    expected = n * (n + 1) // 2
    return expected - sum(nums)
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

