# Basic Calculator II

## Problem

Given a string expression containing non-negative integers and operators `+`, `-`, `*`, `/`, evaluate it. Division truncates toward zero.

## Input

- `s`: arithmetic expression

## Output

- Integer result

## Example

```text
Input: s = "3+2*2"
Output: 7
```

## Intuition

Use a stack for terms. Apply `*` and `/` immediately to the previous term, but push signed values for `+` and `-`.

## Solution

```python
def calculate(s):
    stack = []
    num = 0
    op = "+"

    for i, ch in enumerate(s):
        if ch.isdigit():
            num = num * 10 + int(ch)

        if (not ch.isdigit() and ch != " ") or i == len(s) - 1:
            if op == "+":
                stack.append(num)
            elif op == "-":
                stack.append(-num)
            elif op == "*":
                stack.append(stack.pop() * num)
            else:
                stack.append(int(stack.pop() / num))

            op = ch
            num = 0

    return sum(stack)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

