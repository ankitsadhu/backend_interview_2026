# Subsets

## Problem

Given an integer array `nums` with unique elements, return all possible subsets.

## Input

- `nums`: list of distinct integers

## Output

- List of subsets

## Example

```text
Input: nums = [1, 2, 3]
Output: [[], [1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]]
```

## Intuition

For each number, choose whether to include it or skip it.

## Solution

```python
def subsets(nums):
    ans = []

    def backtrack(i, path):
        if i == len(nums):
            ans.append(path[:])
            return

        backtrack(i + 1, path)

        path.append(nums[i])
        backtrack(i + 1, path)
        path.pop()

    backtrack(0, [])
    return ans
```

## Complexity

- Time: `O(2^n * n)`
- Space: `O(n)` recursion stack, excluding output

