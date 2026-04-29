# Find the Duplicate Number

## Problem

Given an array `nums` containing `n + 1` integers where each integer is in `[1, n]`, return the duplicate number without modifying the array.

## Input

- `nums`: list of integers

## Output

- Duplicate number

## Example

```text
Input: nums = [1,3,4,2,2]
Output: 2
```

## Intuition

Treat each value as a pointer to the next index. A duplicate creates a cycle. Use Floyd's cycle detection to find the cycle entrance.

## Solution

```python
def find_duplicate(nums):
    slow = nums[0]
    fast = nums[0]

    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break

    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]

    return slow
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

