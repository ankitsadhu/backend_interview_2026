# Sort Colors

## Problem

Given an array containing only `0`, `1`, and `2`, sort it in-place.

## Input

- `nums`: list containing `0`, `1`, and `2`

## Output

- Modify `nums` in-place

## Example

```text
Input: nums = [2,0,2,1,1,0]
Output: [0,0,1,1,2,2]
```

## Intuition

Maintain three regions: `0`s before `low`, `2`s after `high`, and unknown values between `mid` and `high`.

## Solution

```python
def sort_colors(nums):
    low = mid = 0
    high = len(nums) - 1

    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

