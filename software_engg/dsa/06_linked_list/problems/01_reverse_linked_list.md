# Reverse Linked List

## Problem

Given the head of a singly linked list, reverse the list and return the new head.

## Input

- `head`: linked list head

## Output

- New head of reversed list

## Example

```text
Input: head = [1,2,3,4,5]
Output: [5,4,3,2,1]
```

## Intuition

Walk through the list and redirect each node's `next` pointer to the previous node.

## Solution

```python
def reverse_list(head):
    prev = None
    curr = head

    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    return prev
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

