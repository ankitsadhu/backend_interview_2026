# Palindrome Linked List

## Problem

Given the head of a singly linked list, return `True` if it is a palindrome.

## Input

- `head`: linked list head

## Output

- Boolean

## Example

```text
Input: head = [1,2,2,1]
Output: True
```

## Intuition

Find the middle, reverse the second half, then compare both halves.

## Solution

```python
def is_palindrome(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    prev = None
    curr = slow
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt

    left, right = head, prev
    while right:
        if left.val != right.val:
            return False
        left = left.next
        right = right.next

    return True
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

