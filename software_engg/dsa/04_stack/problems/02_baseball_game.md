# Baseball Game

## Problem

Given a list of operations, calculate the final score. Integers add a score, `"+"` adds the sum of previous two scores, `"D"` doubles the previous score, and `"C"` removes the previous score.

## Input

- `operations`: list of strings

## Output

- Final score

## Example

```text
Input: ops = ["5","2","C","D","+"]
Output: 30
```

## Intuition

The current operation often depends on recent valid scores, so keep those scores in a stack.

## Solution

```python
def cal_points(operations):
    stack = []

    for op in operations:
        if op == "+":
            stack.append(stack[-1] + stack[-2])
        elif op == "D":
            stack.append(2 * stack[-1])
        elif op == "C":
            stack.pop()
        else:
            stack.append(int(op))

    return sum(stack)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

