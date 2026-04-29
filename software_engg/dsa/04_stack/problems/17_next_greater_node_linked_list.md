# Next Greater Node in Linked List

## Problem

Given the head of a linked list, return an array where each value is the next greater node value for that node, or `0` if none exists.

## Input

- `head`: linked list head

## Output

- List of next greater values

## Example

```text
Input: head = [2,1,5]
Output: [5,5,0]
```

## Intuition

Traverse the list into an array-like sequence. Use a decreasing stack of indices waiting for their next greater value.

## Solution

```python
def next_larger_nodes(head):
    values = []
    while head:
        values.append(head.val)
        head = head.next

    ans = [0] * len(values)
    stack = []

    for i, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            ans[stack.pop()] = value
        stack.append(i)

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

