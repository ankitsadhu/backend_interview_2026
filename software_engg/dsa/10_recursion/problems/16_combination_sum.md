# Combination Sum

## Problem

Given distinct candidates and a target, return all unique combinations where chosen numbers sum to target. A candidate may be used unlimited times.

## Input

- `candidates`: list of distinct positive integers
- `target`: positive integer

## Output

- List of combinations that sum to `target`

## Example

```text
Input: candidates = [2, 3, 6, 7], target = 7
Output: [[2,2,3], [7]]
```

## Intuition

At index `i`, choose the current candidate and stay at `i`, or move to later candidates.

## Solution

```python
def combination_sum(candidates, target):
    candidates.sort()
    ans = []

    def backtrack(start, remaining, path):
        if remaining == 0:
            ans.append(path[:])
            return

        for i in range(start, len(candidates)):
            value = candidates[i]
            if value > remaining:
                break

            path.append(value)
            backtrack(i, remaining - value, path)
            path.pop()

    backtrack(0, target, [])
    return ans
```

## Complexity

- Time: exponential in the number of valid search paths
- Space: `O(target / min(candidates))` recursion stack

