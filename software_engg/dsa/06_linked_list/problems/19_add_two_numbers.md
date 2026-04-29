# Add Two Numbers

## Problem

Given two non-empty linked lists representing non-negative integers in reverse order, add the numbers and return the sum as a linked list.

## Input

- `l1`: first number list
- `l2`: second number list

## Output

- Sum list

## Example

```text
Input: l1 = [2,4,3], l2 = [5,6,4]
Output: [7,0,8]
```

## Intuition

Walk both lists like grade-school addition, carrying overflow to the next digit.

## Solution

```python
def add_two_numbers(l1, l2):
    dummy = ListNode(0)
    tail = dummy
    carry = 0

    while l1 or l2 or carry:
        total = carry
        if l1:
            total += l1.val
            l1 = l1.next
        if l2:
            total += l2.val
            l2 = l2.next

        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next

    return dummy.next
```

## Complexity

- Time: `O(max(n, m))`
- Space: `O(max(n, m))` for output

