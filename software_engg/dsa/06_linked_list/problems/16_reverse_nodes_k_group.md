# Reverse Nodes in k-Group

## Problem

Given a linked list, reverse nodes in groups of `k`. If fewer than `k` nodes remain, leave them unchanged.

## Input

- `head`: linked list head
- `k`: group size

## Output

- Head after group reversals

## Example

```text
Input: head = [1,2,3,4,5], k = 2
Output: [2,1,4,3,5]
```

## Intuition

For each group, first verify that `k` nodes exist. Then reverse the group and connect it to the previous and next sections.

## Solution

```python
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy

    def kth_node(node):
        for _ in range(k):
            node = node.next
            if not node:
                return None
        return node

    while True:
        kth = kth_node(group_prev)
        if not kth:
            break

        group_next = kth.next
        prev = group_next
        curr = group_prev.next

        while curr != group_next:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt

        old_group_start = group_prev.next
        group_prev.next = kth
        group_prev = old_group_start

    return dummy.next
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

