# Sum of Subarray Minimums

## Problem

Given an array `arr`, return the sum of the minimum value of every subarray. Return the answer modulo `10^9 + 7`.

## Input

- `arr`: list of integers

## Output

- Sum of subarray minimums

## Example

```text
Input: arr = [3,1,2,4]
Output: 17
```

## Intuition

For each element, count how many subarrays use it as the minimum. Use previous strictly smaller and next smaller-or-equal boundaries to avoid duplicate counting.

## Solution

```python
def sum_subarray_mins(arr):
    mod = 10**9 + 7
    n = len(arr)
    prev_less = [-1] * n
    next_less_equal = [n] * n
    stack = []

    for i, value in enumerate(arr):
        while stack and arr[stack[-1]] > value:
            stack.pop()
        prev_less[i] = stack[-1] if stack else -1
        stack.append(i)

    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        next_less_equal[i] = stack[-1] if stack else n
        stack.append(i)

    total = 0
    for i, value in enumerate(arr):
        left_count = i - prev_less[i]
        right_count = next_less_equal[i] - i
        total = (total + value * left_count * right_count) % mod

    return total
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

