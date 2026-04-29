# Subarray Sums Divisible by K

## Problem

Given `nums` and `k`, return the number of subarrays whose sum is divisible by `k`.

## Input

- `nums`: list of integers
- `k`: positive integer

## Output

- Count of valid subarrays

## Example

```text
Input: nums = [4,5,0,-2,-3,1], k = 5
Output: 7
```

## Intuition

Two prefix sums with the same remainder create a subarray divisible by `k`.

## Solution

```python
from collections import defaultdict

def subarrays_div_by_k(nums, k):
    freq = defaultdict(int)
    freq[0] = 1
    prefix = 0
    ans = 0

    for num in nums:
        prefix += num
        remainder = prefix % k
        ans += freq[remainder]
        freq[remainder] += 1

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(k)`

