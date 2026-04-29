# Linked List Cycle

## Problem

Given the head of a linked list, return `True` if the list contains a cycle.

## Input

- `head`: linked list head

## Output

- Boolean

## Example

```text
Input: head = [3,2,0,-4], pos = 1
Output: True
```

## Intuition

Use Floyd's cycle detection. If a fast pointer ever meets a slow pointer, there is a cycle.

## Solution

```python
def has_cycle(head):
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

        if slow == fast:
            return True

    return False
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

