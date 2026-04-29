# Find 3-Digit Even Numbers

## Problem

Given an array of digits, return all unique 3-digit even numbers that can be formed using each digit at most once.

## Input

- `digits`: list of digits from `0` to `9`

## Output

- Sorted list of unique 3-digit even numbers

## Example

```text
Input: digits = [2, 1, 3, 0]
Output: [102, 120, 130, 132, 210, 230, 302, 310, 312, 320]
```

## Intuition

Build a 3-length number recursively. The first digit cannot be `0`, and the last digit must be even.

## Solution

```python
def find_even_numbers(digits):
    ans = set()
    used = [False] * len(digits)

    def backtrack(path):
        if len(path) == 3:
            if path[-1] % 2 == 0:
                ans.add(path[0] * 100 + path[1] * 10 + path[2])
            return

        for i, digit in enumerate(digits):
            if used[i]:
                continue
            if len(path) == 0 and digit == 0:
                continue

            used[i] = True
            path.append(digit)
            backtrack(path)
            path.pop()
            used[i] = False

    backtrack([])
    return sorted(ans)
```

## Complexity

- Time: `O(m^3 log m)` for `m = len(digits)` because the number length is fixed at `3`
- Space: `O(m)` plus output

