# Remove Nth Node From End of List

## Problem

Given the head of a linked list, remove the `n`th node from the end and return the head.

## Input

- `head`: linked list head
- `n`: position from end

## Output

- Head after deletion

## Example

```text
Input: head = [1,2,3,4,5], n = 2
Output: [1,2,3,5]
```

## Intuition

Move `fast` `n` steps ahead, then move `slow` and `fast` together. `slow` lands before the node to remove.

## Solution

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy

    for _ in range(n):
        fast = fast.next

    while fast.next:
        slow = slow.next
        fast = fast.next

    slow.next = slow.next.next
    return dummy.next
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

