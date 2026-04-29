# Two Sum II - Input Array Is Sorted

## Problem

Given a 1-indexed sorted array `numbers`, return the indices of two numbers that add up to `target`.

## Input

- `numbers`: sorted list of integers
- `target`: integer

## Output

- 1-indexed pair of indices

## Example

```text
Input: numbers = [2,7,11,15], target = 9
Output: [1,2]
```

## Intuition

If the sum is too small, move the left pointer right. If too large, move the right pointer left.

## Solution

```python
def two_sum(numbers, target):
    left, right = 0, len(numbers) - 1

    while left < right:
        total = numbers[left] + numbers[right]
        if total == target:
            return [left + 1, right + 1]
        if total < target:
            left += 1
        else:
            right -= 1
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

