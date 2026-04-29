# Insert Delete GetRandom O(1)

## Problem

Design a data structure that supports `insert`, `remove`, and `getRandom` in average `O(1)` time.

## Input

- Operations on a randomized set

## Output

- Operation results

## Example

```text
insert(1) -> True
remove(2) -> False
insert(2) -> True
getRandom() -> 1 or 2
remove(1) -> True
```

## Intuition

Use an array for random access and a hash map from value to array index. To remove in `O(1)`, swap the target with the last value and pop.

## Solution

```python
import random

class RandomizedSet:
    def __init__(self):
        self.values = []
        self.index = {}

    def insert(self, val):
        if val in self.index:
            return False
        self.index[val] = len(self.values)
        self.values.append(val)
        return True

    def remove(self, val):
        if val not in self.index:
            return False

        i = self.index[val]
        last = self.values[-1]
        self.values[i] = last
        self.index[last] = i

        self.values.pop()
        del self.index[val]
        return True

    def getRandom(self):
        return random.choice(self.values)
```

## Complexity

- Time: `O(1)` average for each operation
- Space: `O(n)`

