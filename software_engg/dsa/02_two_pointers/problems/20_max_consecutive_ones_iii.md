# Max Consecutive Ones III

## Problem

Given a binary array `nums` and integer `k`, return the maximum number of consecutive `1`s if you can flip at most `k` zeroes.

## Input

- `nums`: list of `0`s and `1`s
- `k`: maximum zeroes to flip

## Output

- Maximum window length

## Example

```text
Input: nums = [1,1,1,0,0,0,1,1,1,1,0], k = 2
Output: 6
```

## Intuition

Maintain a window with at most `k` zeroes. Expand right, and shrink left when the window becomes invalid.

## Solution

```python
def longest_ones(nums, k):
    left = 0
    zeroes = 0
    best = 0

    for right, value in enumerate(nums):
        if value == 0:
            zeroes += 1

        while zeroes > k:
            if nums[left] == 0:
                zeroes -= 1
            left += 1

        best = max(best, right - left + 1)

    return best
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

