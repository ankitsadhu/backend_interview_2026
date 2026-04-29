# Middle of the Linked List

## Problem

Given the head of a linked list, return the middle node. If there are two middle nodes, return the second one.

## Input

- `head`: linked list head

## Output

- Middle node

## Example

```text
Input: head = [1,2,3,4,5]
Output: node with value 3
```

## Intuition

Move `slow` one step and `fast` two steps. When `fast` reaches the end, `slow` is at the middle.

## Solution

```python
def middle_node(head):
    slow = fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

