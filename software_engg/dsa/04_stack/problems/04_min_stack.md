# Min Stack

## Problem

Design a stack that supports `push`, `pop`, `top`, and `getMin` in constant time.

## Input

- Stack operations

## Output

- Operation results

## Example

```text
push(-2), push(0), push(-3), getMin() -> -3
pop(), top() -> 0, getMin() -> -2
```

## Intuition

Store the current minimum alongside each pushed value.

## Solution

```python
class MinStack:
    def __init__(self):
        self.stack = []

    def push(self, val):
        current_min = val if not self.stack else min(val, self.stack[-1][1])
        self.stack.append((val, current_min))

    def pop(self):
        self.stack.pop()

    def top(self):
        return self.stack[-1][0]

    def getMin(self):
        return self.stack[-1][1]
```

## Complexity

- Time: `O(1)` per operation
- Space: `O(n)`

