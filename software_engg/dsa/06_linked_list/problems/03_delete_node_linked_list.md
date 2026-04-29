# Delete Node in a Linked List

## Problem

Given only a node to delete from a singly linked list, delete it. The node is not the tail.

## Input

- `node`: node to delete

## Output

- Modify the list in-place

## Example

```text
Input: head = [4,5,1,9], node = 5
Output: [4,1,9]
```

## Intuition

Since we do not have the previous node, copy the next node's value into the current node, then skip the next node.

## Solution

```python
def delete_node(node):
    node.val = node.next.val
    node.next = node.next.next
```

## Complexity

- Time: `O(1)`
- Space: `O(1)`

