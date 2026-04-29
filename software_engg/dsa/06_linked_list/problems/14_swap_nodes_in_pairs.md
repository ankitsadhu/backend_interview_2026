# Swap Nodes in Pairs

## Problem

Given a linked list, swap every two adjacent nodes and return the head.

## Input

- `head`: linked list head

## Output

- Head after pair swaps

## Example

```text
Input: head = [1,2,3,4]
Output: [2,1,4,3]
```

## Intuition

Use a dummy node before each pair. Rewire `first` and `second`, then move to the next pair.

## Solution

```python
def swap_pairs(head):
    dummy = ListNode(0, head)
    prev = dummy

    while prev.next and prev.next.next:
        first = prev.next
        second = first.next

        first.next = second.next
        second.next = first
        prev.next = second

        prev = first

    return dummy.next
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

