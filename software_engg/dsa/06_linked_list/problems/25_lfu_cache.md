# LFU Cache

## Problem

Design an LFU cache with `get` and `put`. When capacity is exceeded, evict the least frequently used key. If tied, evict the least recently used among them.

## Input

- Cache operations

## Output

- Operation results

## Example

```text
LFUCache(2)
put(1,1), put(2,2), get(1) -> 1
put(3,3) evicts key 2
get(2) -> -1
```

## Intuition

Track each key's value and frequency. For each frequency, keep an ordered dictionary of keys to preserve recency.

## Solution

```python
from collections import defaultdict, OrderedDict

class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.min_freq = 0
        self.key_to_value_freq = {}
        self.freq_to_keys = defaultdict(OrderedDict)

    def _touch(self, key):
        value, freq = self.key_to_value_freq[key]
        del self.freq_to_keys[freq][key]

        if not self.freq_to_keys[freq]:
            del self.freq_to_keys[freq]
            if self.min_freq == freq:
                self.min_freq += 1

        new_freq = freq + 1
        self.freq_to_keys[new_freq][key] = None
        self.key_to_value_freq[key] = (value, new_freq)

    def get(self, key):
        if key not in self.key_to_value_freq:
            return -1

        self._touch(key)
        return self.key_to_value_freq[key][0]

    def put(self, key, value):
        if self.capacity == 0:
            return

        if key in self.key_to_value_freq:
            self.key_to_value_freq[key] = (value, self.key_to_value_freq[key][1])
            self._touch(key)
            return

        if len(self.key_to_value_freq) == self.capacity:
            evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            del self.key_to_value_freq[evict_key]
            if not self.freq_to_keys[self.min_freq]:
                del self.freq_to_keys[self.min_freq]

        self.key_to_value_freq[key] = (value, 1)
        self.freq_to_keys[1][key] = None
        self.min_freq = 1
```

## Complexity

- Time: `O(1)` average per operation
- Space: `O(capacity)`

