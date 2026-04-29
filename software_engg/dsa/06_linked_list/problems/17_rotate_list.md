# Rotate List

## Problem

Given a linked list, rotate it to the right by `k` places.

## Input

- `head`: linked list head
- `k`: number of rotations

## Output

- Rotated list head

## Example

```text
Input: head = [1,2,3,4,5], k = 2
Output: [4,5,1,2,3]
```

## Intuition

Connect the list into a cycle. The new tail is `length - k % length - 1` steps from the original head.

## Solution

```python
def rotate_right(head, k):
    if not head or not head.next:
        return head

    length = 1
    tail = head
    while tail.next:
        tail = tail.next
        length += 1

    k %= length
    if k == 0:
        return head

    tail.next = head
    steps_to_new_tail = length - k - 1
    new_tail = head

    for _ in range(steps_to_new_tail):
        new_tail = new_tail.next

    new_head = new_tail.next
    new_tail.next = None
    return new_head
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

