# Remove Element

## Problem

Given an array `nums` and a value `val`, remove all instances of `val` in-place and return the new length.

## Input

- `nums`: list of integers
- `val`: value to remove

## Output

- New length `k`; first `k` elements of `nums` contain the remaining values

## Example

```text
Input: nums = [3,2,2,3], val = 3
Output: 2, nums starts with [2,2]
```

## Intuition

Use a write pointer for the next kept value.

## Solution

```python
def remove_element(nums, val):
    write = 0

    for num in nums:
        if num != val:
            nums[write] = num
            write += 1

    return write
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

