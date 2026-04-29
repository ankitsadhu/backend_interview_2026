# Permutations

## Problem

Given an array of distinct integers, return all possible permutations.

## Input

- `nums`: list of distinct integers

## Output

- List of permutations

## Example

```text
Input: nums = [1, 2, 3]
Output: [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
```

## Intuition

At each position, try every unused number.

## Solution

```python
def permute(nums):
    ans = []
    used = [False] * len(nums)

    def backtrack(path):
        if len(path) == len(nums):
            ans.append(path[:])
            return

        for i, value in enumerate(nums):
            if used[i]:
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

- Time: `O(n! * n)`
- Space: `O(n)` recursion stack, excluding output

