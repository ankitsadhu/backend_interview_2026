# Subsets II

## Problem

Given an integer array `nums` that may contain duplicates, return all possible unique subsets.

## Input

- `nums`: list of integers

## Output

- List of unique subsets

## Example

```text
Input: nums = [1, 2, 2]
Output: [[], [1], [1,2], [1,2,2], [2], [2,2]]
```

## Intuition

Sort first. At the same recursion depth, skip a duplicate value if the previous equal value was already skipped.

## Solution

```python
def subsets_with_dup(nums):
    nums.sort()
    ans = []

    def backtrack(start, path):
        ans.append(path[:])

        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue

            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return ans
```

## Complexity

- Time: `O(2^n * n)`
- Space: `O(n)` recursion stack, excluding output

