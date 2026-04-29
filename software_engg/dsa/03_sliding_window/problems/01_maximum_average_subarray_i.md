# Maximum Average Subarray I

## Problem

Given an integer array `nums` and integer `k`, find the maximum average value of any contiguous subarray of length `k`.

## Input

- `nums`: list of integers
- `k`: window size

## Output

- Maximum average

## Example

```text
Input: nums = [1,12,-5,-6,50,3], k = 4
Output: 12.75
```

## Intuition

Maintain the sum of a fixed-size window. Slide by adding the new right value and removing the old left value.

## Solution

```python
def find_max_average(nums, k):
    window_sum = sum(nums[:k])
    best = window_sum

    for right in range(k, len(nums)):
        window_sum += nums[right] - nums[right - k]
        best = max(best, window_sum)

    return best / k
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

