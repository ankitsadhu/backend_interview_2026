# Find K Closest Elements

## Problem

Given a sorted array `arr`, integers `k` and `x`, return the `k` closest elements to `x` in sorted order.

## Input

- `arr`: sorted list of integers
- `k`: number of elements
- `x`: target value

## Output

- Sorted list of `k` closest elements

## Example

```text
Input: arr = [1,2,3,4,5], k = 4, x = 3
Output: [1,2,3,4]
```

## Intuition

The answer is always a contiguous window of length `k`. Binary search the left boundary of that window.

## Solution

```python
def find_closest_elements(arr, k, x):
    left, right = 0, len(arr) - k

    while left < right:
        mid = left + (right - left) // 2

        if x - arr[mid] > arr[mid + k] - x:
            left = mid + 1
        else:
            right = mid

    return arr[left:left + k]
```

## Complexity

- Time: `O(log(n - k) + k)`
- Space: `O(k)` for output

