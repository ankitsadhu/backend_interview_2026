# Partition List

## Problem

Given a linked list and value `x`, partition it so nodes less than `x` come before nodes greater than or equal to `x`, preserving original relative order.

## Input

- `head`: linked list head
- `x`: partition value

## Output

- Head of partitioned list

## Example

```text
Input: head = [1,4,3,2,5,2], x = 3
Output: [1,2,2,4,3,5]
```

## Intuition

Build two lists: one for nodes less than `x`, and one for the rest. Connect them at the end.

## Solution

```python
def partition(head, x):
    before_dummy = ListNode(0)
    after_dummy = ListNode(0)
    before = before_dummy
    after = after_dummy

    curr = head
    while curr:
        if curr.val < x:
            before.next = curr
            before = before.next
        else:
            after.next = curr
            after = after.next
        curr = curr.next

    after.next = None
    before.next = after_dummy.next
    return before_dummy.next
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

