# Time Based Key-Value Store

## Problem

Design a time-based key-value store that supports:

- `set(key, value, timestamp)`
- `get(key, timestamp)`: return the value with the largest timestamp less than or equal to `timestamp`

## Input

- Operations on `TimeMap`

## Output

- Operation results

## Example

```text
set("foo", "bar", 1)
get("foo", 1) -> "bar"
get("foo", 3) -> "bar"
set("foo", "bar2", 4)
get("foo", 4) -> "bar2"
get("foo", 5) -> "bar2"
```

## Intuition

For each key, values are stored by increasing timestamp. Use binary search to find the rightmost timestamp `<=` query timestamp.

## Solution

```python
from collections import defaultdict

class TimeMap:
    def __init__(self):
        self.store = defaultdict(list)

    def set(self, key, value, timestamp):
        self.store[key].append((timestamp, value))

    def get(self, key, timestamp):
        values = self.store[key]
        left, right = 0, len(values) - 1
        answer = ""

        while left <= right:
            mid = left + (right - left) // 2
            if values[mid][0] <= timestamp:
                answer = values[mid][1]
                left = mid + 1
            else:
                right = mid - 1

        return answer
```

## Complexity

- `set`: `O(1)`
- `get`: `O(log n)`
- Space: `O(n)`

