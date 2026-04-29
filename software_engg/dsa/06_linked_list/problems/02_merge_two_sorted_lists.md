# Merge Two Sorted Lists

## Problem

Given two sorted linked lists, merge them into one sorted linked list.

## Input

- `list1`: head of first sorted list
- `list2`: head of second sorted list

## Output

- Head of merged sorted list

## Example

```text
Input: list1 = [1,2,4], list2 = [1,3,4]
Output: [1,1,2,3,4,4]
```

## Intuition

Use a dummy node and attach the smaller current node from either list.

## Solution

```python
def merge_two_lists(list1, list2):
    dummy = ListNode(0)
    tail = dummy

    while list1 and list2:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next

    tail.next = list1 or list2
    return dummy.next
```

## Complexity

- Time: `O(n + m)`
- Space: `O(1)`

