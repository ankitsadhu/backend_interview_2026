# Decode String

## Problem

Given an encoded string, decode it. The format is `k[encoded_string]`, where the substring inside brackets is repeated `k` times.

## Input

- `s`: encoded string

## Output

- Decoded string

## Example

```text
Input: s = "3[a2[c]]"
Output: "accaccacc"
```

## Intuition

When `[` appears, save the current string and repeat count. When `]` appears, pop that context and expand.

## Solution

```python
def decode_string(s):
    stack = []
    current = []
    number = 0

    for ch in s:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch == "[":
            stack.append(("".join(current), number))
            current = []
            number = 0
        elif ch == "]":
            previous, repeat = stack.pop()
            current = [previous + "".join(current) * repeat]
        else:
            current.append(ch)

    return "".join(current)
```

## Complexity

- Time: `O(output length)`
- Space: `O(output length)`

