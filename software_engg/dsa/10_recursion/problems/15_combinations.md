# Combinations

## Problem

Given two integers `n` and `k`, return all combinations of `k` numbers chosen from `1` to `n`.

## Input

- `n`: upper bound
- `k`: combination size

## Output

- List of combinations

## Example

```text
Input: n = 4, k = 2
Output: [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
```

## Intuition

Build combinations in increasing order so the same group is never generated twice.

## Solution

```python
def combine(n, k):
    ans = []

    def backtrack(start, path):
        if len(path) == k:
            ans.append(path[:])
            return

        remaining_needed = k - len(path)
        for num in range(start, n - remaining_needed + 2):
            path.append(num)
            backtrack(num + 1, path)
            path.pop()

    backtrack(1, [])
    return ans
```

## Complexity

- Time: `O(C(n, k) * k)`
- Space: `O(k)` recursion stack, excluding output

