# Remove Duplicates from Sorted List

## Problem

Given the head of a sorted linked list, delete duplicate nodes so each value appears once.

## Input

- `head`: sorted linked list head

## Output

- Head of deduplicated list

## Example

```text
Input: head = [1,1,2,3,3]
Output: [1,2,3]
```

## Intuition

Because duplicates are adjacent, skip the next node whenever it has the same value as the current node.

## Solution

```python
def delete_duplicates(head):
    curr = head

    while curr and curr.next:
        if curr.val == curr.next.val:
            curr.next = curr.next.next
        else:
            curr = curr.next

    return head
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

