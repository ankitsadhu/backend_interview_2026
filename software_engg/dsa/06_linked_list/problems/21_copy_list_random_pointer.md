# Copy List with Random Pointer

## Problem

Given a linked list where each node has `next` and `random` pointers, create a deep copy of the list.

## Input

- `head`: linked list head with random pointers

## Output

- Head of copied list

## Example

```text
Input: head = [[7,null],[13,0],[11,4],[10,2],[1,0]]
Output: deep copy with same values and random relationships
```

## Intuition

Map each original node to its clone. Then assign `next` and `random` pointers using the map.

## Solution

```python
def copy_random_list(head):
    if not head:
        return None

    clone = {}
    curr = head
    while curr:
        clone[curr] = Node(curr.val)
        curr = curr.next

    curr = head
    while curr:
        clone[curr].next = clone.get(curr.next)
        clone[curr].random = clone.get(curr.random)
        curr = curr.next

    return clone[head]
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

