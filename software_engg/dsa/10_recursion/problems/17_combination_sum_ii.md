# Combination Sum II

## Problem

Given candidates that may contain duplicates and a target, return all unique combinations where each candidate can be used at most once.

## Input

- `candidates`: list of positive integers
- `target`: positive integer

## Output

- List of unique combinations that sum to `target`

## Example

```text
Input: candidates = [10,1,2,7,6,1,5], target = 8
Output: [[1,1,6], [1,2,5], [1,7], [2,6]]
```

## Intuition

Sort first. Skip duplicates at the same depth so identical combinations are not regenerated.

## Solution

```python
def combination_sum2(candidates, target):
    candidates.sort()
    ans = []

    def backtrack(start, remaining, path):
        if remaining == 0:
            ans.append(path[:])
            return

        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue

            value = candidates[i]
            if value > remaining:
                break

            path.append(value)
            backtrack(i + 1, remaining - value, path)
            path.pop()

    backtrack(0, target, [])
    return ans
```

## Complexity

- Time: `O(2^n * n)` worst case
- Space: `O(n)` recursion stack

