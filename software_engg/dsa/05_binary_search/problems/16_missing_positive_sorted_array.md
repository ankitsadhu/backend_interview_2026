# Missing Positive Number in Sorted Array

## Problem

Given a sorted array of positive distinct integers and integer `k`, return the `k`th missing positive number.

## Input

- `arr`: sorted list of positive distinct integers
- `k`: missing number position

## Output

- The `k`th missing positive number

## Example

```text
Input: arr = [2,3,4,7,11], k = 5
Output: 9
```

## Intuition

At index `i`, the count of missing positive numbers before or at `arr[i]` is `arr[i] - (i + 1)`. Find the first index where this count is at least `k`.

## Solution

```python
def find_kth_positive(arr, k):
    left, right = 0, len(arr)

    while left < right:
        mid = left + (right - left) // 2
        missing = arr[mid] - (mid + 1)

        if missing < k:
            left = mid + 1
        else:
            right = mid

    return left + k
```

## Complexity

- Time: `O(log n)`
- Space: `O(1)`

