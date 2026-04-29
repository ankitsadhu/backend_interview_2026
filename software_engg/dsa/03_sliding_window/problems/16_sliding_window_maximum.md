# Sliding Window Maximum

## Problem

Given an array `nums` and window size `k`, return the maximum value in each sliding window.

## Input

- `nums`: list of integers
- `k`: window size

## Output

- List of maximums

## Example

```text
Input: nums = [1,3,-1,-3,5,3,6,7], k = 3
Output: [3,3,5,5,6,7]
```

## Intuition

Use a decreasing deque of indices. The front always points to the maximum value in the current window.

## Solution

```python
from collections import deque

def max_sliding_window(nums, k):
    dq = deque()
    ans = []

    for right, value in enumerate(nums):
        while dq and nums[dq[-1]] <= value:
            dq.pop()
        dq.append(right)

        if dq[0] <= right - k:
            dq.popleft()

        if right >= k - 1:
            ans.append(nums[dq[0]])

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(k)`

