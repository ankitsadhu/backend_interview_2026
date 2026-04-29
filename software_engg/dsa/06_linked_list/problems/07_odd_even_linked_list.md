# Odd Even Linked List

## Problem

Given a linked list, group all nodes at odd indices followed by nodes at even indices. Indices are 1-based.

## Input

- `head`: linked list head

## Output

- Reordered list head

## Example

```text
Input: head = [1,2,3,4,5]
Output: [1,3,5,2,4]
```

## Intuition

Maintain separate odd and even chains, then attach the even chain after the odd chain.

## Solution

```python
def odd_even_list(head):
    if not head:
        return None

    odd = head
    even = head.next
    even_head = even

    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next

    odd.next = even_head
    return head
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

