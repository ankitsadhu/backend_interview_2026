# Remove Duplicates from Sorted Array

## Problem

Given a sorted array `nums`, remove duplicates in-place so each unique value appears once. Return the number of unique values.

## Input

- `nums`: sorted list of integers

## Output

- New length `k`

## Example

```text
Input: nums = [1,1,2]
Output: 2, nums starts with [1,2]
```

## Intuition

Because the array is sorted, a value is new only when it differs from the previous value.

## Solution

```python
def remove_duplicates(nums):
    if not nums:
        return 0

    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[read - 1]:
            nums[write] = nums[read]
            write += 1

    return write
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

