# Combination Sum III

## Problem

Find all valid combinations of `k` numbers that sum to `n`. Only numbers `1` to `9` can be used, and each number can be used at most once.

## Input

- `k`: number of values to choose
- `n`: required sum

## Output

- List of valid combinations

## Example

```text
Input: k = 3, n = 7
Output: [[1,2,4]]
```

## Intuition

This is combinations with two stopping conditions: path length and remaining sum.

## Solution

```python
def combination_sum3(k, n):
    ans = []

    def backtrack(start, remaining, path):
        if len(path) == k:
            if remaining == 0:
                ans.append(path[:])
            return

        for num in range(start, 10):
            if num > remaining:
                break

            path.append(num)
            backtrack(num + 1, remaining - num, path)
            path.pop()

    backtrack(1, n, [])
    return ans
```

## Complexity

- Time: `O(C(9, k) * k)`
- Space: `O(k)` recursion stack

