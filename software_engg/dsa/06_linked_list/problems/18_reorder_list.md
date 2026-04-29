# Reorder List

## Problem

Given a linked list `L0 -> L1 -> ... -> Ln`, reorder it to `L0 -> Ln -> L1 -> Ln-1 -> ...` in-place.

## Input

- `head`: linked list head

## Output

- Modify list in-place

## Example

```text
Input: head = [1,2,3,4]
Output: [1,4,2,3]
```

## Intuition

Find the middle, reverse the second half, then merge the two halves alternately.

## Solution

```python
def reorder_list(head):
    if not head or not head.next:
        return

    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    second = slow.next
    slow.next = None

    prev = None
    curr = second
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    first, second = head, prev
    while second:
        tmp1 = first.next
        tmp2 = second.next
        first.next = second
        second.next = tmp1
        first = tmp1
        second = tmp2
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

