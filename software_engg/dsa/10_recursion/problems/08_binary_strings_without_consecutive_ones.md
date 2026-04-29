# Binary Strings Without Consecutive 1s

## Problem

Generate all binary strings of length `n` that do not contain consecutive `1`s.

## Input

- `n`: length of each binary string

## Output

- List of valid binary strings

## Example

```text
Input: n = 3
Output: ["000", "001", "010", "100", "101"]
```

## Intuition

At every position, `0` is always allowed. `1` is allowed only if the previous character was not `1`.

## Solution

```python
def generate_binary_strings(n):
    ans = []

    def backtrack(path, prev_one):
        if len(path) == n:
            ans.append("".join(path))
            return

        path.append("0")
        backtrack(path, False)
        path.pop()

        if not prev_one:
            path.append("1")
            backtrack(path, True)
            path.pop()

    backtrack([], False)
    return ans
```

## Complexity

- Time: `O(2^n)` worst case
- Space: `O(n)` recursion stack, excluding output

