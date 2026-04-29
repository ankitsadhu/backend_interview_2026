# Move Zeroes

## Problem

Given an array `nums`, move all zeroes to the end while maintaining the relative order of non-zero elements.

## Input

- `nums`: list of integers

## Output

- Modify `nums` in-place

## Example

```text
Input: nums = [0,1,0,3,12]
Output: [1,3,12,0,0]
```

## Intuition

Compact non-zero values at the front, then fill the rest with zeroes.

## Solution

```python
def move_zeroes(nums):
    write = 0

    for num in nums:
        if num != 0:
            nums[write] = num
            write += 1

    for i in range(write, len(nums)):
        nums[i] = 0
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

