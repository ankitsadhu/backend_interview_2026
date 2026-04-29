# Contiguous Array

## Problem

Given a binary array `nums`, return the maximum length of a contiguous subarray with equal number of `0`s and `1`s.

## Input

- `nums`: list of `0`s and `1`s

## Output

- Maximum balanced subarray length

## Example

```text
Input: nums = [0, 1, 0]
Output: 2
```

## Intuition

Treat `0` as `-1` and `1` as `+1`. Equal counts mean the prefix balance repeats.

## Solution

```python
def find_max_length(nums):
    first_index = {0: -1}
    balance = 0
    best = 0

    for i, num in enumerate(nums):
        balance += 1 if num == 1 else -1

        if balance in first_index:
            best = max(best, i - first_index[balance])
        else:
            first_index[balance] = i

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

