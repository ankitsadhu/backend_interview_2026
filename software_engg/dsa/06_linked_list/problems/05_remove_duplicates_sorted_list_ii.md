# Remove Duplicates from Sorted List II

## Problem

Given the head of a sorted linked list, delete all nodes that have duplicate values, leaving only distinct values.

## Input

- `head`: sorted linked list head

## Output

- Head of list containing only unique values

## Example

```text
Input: head = [1,2,3,3,4,4,5]
Output: [1,2,5]
```

## Intuition

Use a dummy node before the head. When a duplicate run is found, skip the entire run.

## Solution

```python
def delete_duplicates(head):
    dummy = ListNode(0, head)
    prev = dummy
    curr = head

    while curr:
        duplicate = False
        while curr.next and curr.val == curr.next.val:
            curr = curr.next
            duplicate = True

        if duplicate:
            prev.next = curr.next
        else:
            prev = prev.next

        curr = curr.next

    return dummy.next
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

