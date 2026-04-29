# Continuous Subarray Sum

## Problem

Given `nums` and `k`, return `True` if there is a subarray of length at least `2` whose sum is a multiple of `k`.

## Input

- `nums`: list of integers
- `k`: integer

## Output

- Boolean

## Example

```text
Input: nums = [23,2,4,6,7], k = 6
Output: True
```

## Intuition

If two prefix sums have the same remainder modulo `k`, the subarray between them has sum divisible by `k`.

## Solution

```python
def check_subarray_sum(nums, k):
    first_index = {0: -1}
    prefix = 0

    for i, num in enumerate(nums):
        prefix += num
        remainder = prefix % k

        if remainder in first_index:
            if i - first_index[remainder] >= 2:
                return True
        else:
            first_index[remainder] = i

    return False
```

## Complexity

- Time: `O(n)`
- Space: `O(min(n, k))`

