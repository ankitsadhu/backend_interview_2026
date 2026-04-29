# Intersection of Two Linked Lists

## Problem

Given heads of two singly linked lists, return the node where they intersect, or `None`.

## Input

- `headA`: first list head
- `headB`: second list head

## Output

- Intersection node or `None`

## Example

```text
Input: listA = [4,1,8,4,5], listB = [5,6,1,8,4,5]
Output: node with value 8
```

## Intuition

Switch each pointer to the other list when it reaches the end. Both pointers travel the same total distance.

## Solution

```python
def get_intersection_node(headA, headB):
    a, b = headA, headB

    while a != b:
        a = headB if a is None else a.next
        b = headA if b is None else b.next

    return a
```

## Complexity

- Time: `O(n + m)`
- Space: `O(1)`

