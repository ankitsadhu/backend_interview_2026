# Minimum Number of K Consecutive Bit Flips

## Problem

Given a binary array `nums` and integer `k`, return the minimum number of length-`k` flips needed to make all values `1`. Return `-1` if impossible.

## Input

- `nums`: list of `0`s and `1`s
- `k`: flip length

## Output

- Minimum flips or `-1`

## Example

```text
Input: nums = [0,1,0], k = 1
Output: 2
```

## Intuition

Scan left to right. If the current bit is effectively `0`, we must start a flip here. Track when previous flips expire.

## Solution

```python
def min_k_bit_flips(nums, k):
    n = len(nums)
    flipped = [0] * n
    active_flips = 0
    ans = 0

    for i in range(n):
        if i >= k:
            active_flips ^= flipped[i - k]

        effective = nums[i] ^ active_flips
        if effective == 0:
            if i + k > n:
                return -1

            flipped[i] = 1
            active_flips ^= 1
            ans += 1

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

