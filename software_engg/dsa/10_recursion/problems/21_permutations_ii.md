# Permutations II

## Problem

Given an array that may contain duplicates, return all unique permutations.

## Input

- `nums`: list of integers

## Output

- List of unique permutations

## Example

```text
Input: nums = [1, 1, 2]
Output: [[1,1,2], [1,2,1], [2,1,1]]
```

## Intuition

Sort first. If the previous equal value has not been used in the current path, skip the current value to avoid duplicate orderings.

## Solution

```python
def permute_unique(nums):
    nums.sort()
    ans = []
    used = [False] * len(nums)

    def backtrack(path):
        if len(path) == len(nums):
            ans.append(path[:])
            return

        for i, value in enumerate(nums):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue

            used[i] = True
            path.append(value)
            backtrack(path)
            path.pop()
            used[i] = False

    backtrack([])
    return ans
```

## Complexity

- Time: `O(n! * n)` worst case
- Space: `O(n)` recursion stack, excluding output

