# Two Sum

## Problem

Given `nums` and `target`, return indices of two numbers whose sum is `target`.

## Input

- `nums`: list of integers
- `target`: integer

## Output

- Two indices

## Example

```text
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
```

## Intuition

For each number, check whether its complement has already appeared.

## Solution

```python
def two_sum(nums, target):
    index_by_value = {}

    for i, num in enumerate(nums):
        need = target - num
        if need in index_by_value:
            return [index_by_value[need], i]
        index_by_value[num] = i
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

