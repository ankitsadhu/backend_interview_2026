# Longest Consecutive Sequence

## Problem

Given an unsorted array, return the length of the longest consecutive elements sequence.

## Input

- `nums`: list of integers

## Output

- Length of longest consecutive sequence

## Example

```text
Input: nums = [100,4,200,1,3,2]
Output: 4
```

## Intuition

Only start counting from numbers that have no previous neighbor `num - 1`.

## Solution

```python
def longest_consecutive(nums):
    values = set(nums)
    best = 0

    for num in values:
        if num - 1 in values:
            continue

        length = 1
        while num + length in values:
            length += 1
        best = max(best, length)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

