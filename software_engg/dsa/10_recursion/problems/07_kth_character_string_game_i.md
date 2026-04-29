# 3304. Find the K-th Character in String Game I

## Problem

Start with `word = "a"`. In each operation, create a new string by changing every character of `word` to the next character in the alphabet, then append it to `word`. Return the `k`th character after enough operations.

## Input

- `k`: 1-indexed position

## Output

- Character at position `k`

## Example

```text
Input: k = 5
Output: "b"
```

## Intuition

The string doubles every operation. If `k` lies in the second half, it corresponds to `k - half` in the previous string, shifted by one character.

## Solution

```python
def kth_character(k):
    def dfs(length, index):
        if length == 1:
            return 0

        half = length // 2
        if index <= half:
            return dfs(half, index)
        return dfs(half, index - half) + 1

    length = 1
    while length < k:
        length *= 2

    shift = dfs(length, k)
    return chr(ord("a") + shift)
```

## Complexity

- Time: `O(log k)`
- Space: `O(log k)`

