# Flatten a Multilevel Doubly Linked List

## Problem

Given a multilevel doubly linked list where nodes may have a `child` pointer, flatten it into a single-level doubly linked list.

## Input

- `head`: multilevel doubly linked list head

## Output

- Flattened list head

## Example

```text
Input: 1-2-3-4-5-6, with 3 child 7-8-9-10
Output: 1-2-3-7-8-9-10-4-5-6
```

## Intuition

Use a stack to process next nodes after child chains. Child nodes should come immediately after their parent.

## Solution

```python
def flatten(head):
    if not head:
        return None

    stack = [head]
    prev = None

    while stack:
        curr = stack.pop()

        if prev:
            prev.next = curr
            curr.prev = prev

        if curr.next:
            stack.append(curr.next)
        if curr.child:
            stack.append(curr.child)
            curr.child = None

        prev = curr

    return head
```

## Complexity

- Time: `O(n)`
- Space: `O(n)` worst case

