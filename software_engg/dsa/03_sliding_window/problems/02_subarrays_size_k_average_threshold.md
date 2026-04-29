# Number of Sub-arrays of Size K and Average >= Threshold

## Problem

Given an array `arr`, window size `k`, and `threshold`, return the number of subarrays of size `k` whose average is at least `threshold`.

## Input

- `arr`: list of integers
- `k`: window size
- `threshold`: minimum average

## Output

- Count of valid windows

## Example

```text
Input: arr = [2,2,2,2,5,5,5,8], k = 3, threshold = 4
Output: 3
```

## Intuition

Avoid floating point by comparing window sum with `k * threshold`.

## Solution

```python
def num_of_subarrays(arr, k, threshold):
    target = k * threshold
    window_sum = sum(arr[:k])
    count = 1 if window_sum >= target else 0

    for right in range(k, len(arr)):
        window_sum += arr[right] - arr[right - k]
        if window_sum >= target:
            count += 1

    return count
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

