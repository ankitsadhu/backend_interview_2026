# Evaluate Reverse Polish Notation

## Problem

Evaluate an arithmetic expression in Reverse Polish Notation.

## Input

- `tokens`: list of numbers and operators `+`, `-`, `*`, `/`

## Output

- Integer result

## Example

```text
Input: tokens = ["2","1","+","3","*"]
Output: 9
```

## Intuition

Operands wait on the stack until an operator appears. Then pop the two most recent operands, evaluate, and push the result.

## Solution

```python
def eval_rpn(tokens):
    stack = []

    for token in tokens:
        if token not in {"+", "-", "*", "/"}:
            stack.append(int(token))
            continue

        b = stack.pop()
        a = stack.pop()

        if token == "+":
            stack.append(a + b)
        elif token == "-":
            stack.append(a - b)
        elif token == "*":
            stack.append(a * b)
        else:
            stack.append(int(a / b))

    return stack[-1]
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

