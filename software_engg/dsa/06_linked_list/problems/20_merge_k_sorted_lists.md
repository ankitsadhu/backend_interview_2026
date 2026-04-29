# Merge K Sorted Lists

## Problem

Given an array of `k` sorted linked lists, merge them into one sorted linked list.

## Input

- `lists`: list of linked list heads

## Output

- Head of merged sorted list

## Example

```text
Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
```

## Intuition

Use a min-heap containing the current smallest node from each list.

## Solution

```python
import heapq

def merge_k_lists(lists):
    heap = []

    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode(0)
    tail = dummy

    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next

        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next
```

## Complexity

- Time: `O(n log k)`, where `n` is total nodes
- Space: `O(k)`

