# Basic Calculator

## Problem

Given a string expression containing non-negative integers, `+`, `-`, parentheses, and spaces, evaluate it.

## Input

- `s`: arithmetic expression

## Output

- Integer result

## Example

```text
Input: s = "(1+(4+5+2)-3)+(6+8)"
Output: 23
```

## Intuition

Track the current result and sign. When `(` appears, push the previous result and sign. When `)` appears, collapse the current result into the previous context.

## Solution

```python
def calculate(s):
    stack = []
    result = 0
    number = 0
    sign = 1

    for ch in s:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch in "+-":
            result += sign * number
            number = 0
            sign = 1 if ch == "+" else -1
        elif ch == "(":
            stack.append(result)
            stack.append(sign)
            result = 0
            sign = 1
        elif ch == ")":
            result += sign * number
            number = 0
            previous_sign = stack.pop()
            previous_result = stack.pop()
            result = previous_result + previous_sign * result

    return result + sign * number
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

