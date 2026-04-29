# Tower of Hanoi

## Problem

Given `n` disks on source rod `A`, move all disks to destination rod `C` using helper rod `B`. Only one disk can be moved at a time, and a larger disk cannot be placed on a smaller disk.

## Input

- `n`: number of disks

## Output

- Sequence of moves

## Example

```text
Input: n = 2
Output:
A -> B
A -> C
B -> C
```

## Intuition

Move `n - 1` disks to the helper, move the largest disk to destination, then move `n - 1` disks from helper to destination.

## Solution

```python
def tower_of_hanoi(n):
    moves = []

    def solve(disks, source, helper, destination):
        if disks == 0:
            return

        solve(disks - 1, source, destination, helper)
        moves.append((source, destination))
        solve(disks - 1, helper, source, destination)

    solve(n, "A", "B", "C")
    return moves
```

## Complexity

- Time: `O(2^n)`
- Space: `O(n)` recursion stack

