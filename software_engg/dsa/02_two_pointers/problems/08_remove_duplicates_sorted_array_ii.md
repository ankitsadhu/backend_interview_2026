# Remove Duplicates from Sorted Array II

## Problem

Given a sorted array `nums`, remove duplicates in-place so each unique value appears at most twice. Return the new length.

## Input

- `nums`: sorted list of integers

## Output

- New length `k`

## Example

```text
Input: nums = [0,0,1,1,1,1,2,3,3]
Output: 7, nums starts with [0,0,1,1,2,3,3]
```

## Intuition

When writing a value, compare it with the value two positions behind the write pointer. If they are different, this value is allowed.

## Solution

```python
def remove_duplicates(nums):
    write = 0

    for num in nums:
        if write < 2 or num != nums[write - 2]:
            nums[write] = num
            write += 1

    return write
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

