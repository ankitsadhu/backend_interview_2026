# Reverse Linked List II

## Problem

Given the head of a linked list and positions `left` and `right`, reverse the nodes from `left` to `right` in-place.

## Input

- `head`: linked list head
- `left`: start position
- `right`: end position

## Output

- Head after partial reversal

## Example

```text
Input: head = [1,2,3,4,5], left = 2, right = 4
Output: [1,4,3,2,5]
```

## Intuition

Move to the node before `left`, then repeatedly move the next node after the reversed segment to the front.

## Solution

```python
def reverse_between(head, left, right):
    dummy = ListNode(0, head)
    prev = dummy

    for _ in range(left - 1):
        prev = prev.next

    curr = prev.next
    for _ in range(right - left):
        nxt = curr.next
        curr.next = nxt.next
        nxt.next = prev.next
        prev.next = nxt

    return dummy.next
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

