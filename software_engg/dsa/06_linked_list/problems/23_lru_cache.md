# LRU Cache

## Problem

Design an LRU cache with `get` and `put` in `O(1)` average time. When capacity is exceeded, evict the least recently used key.

## Input

- Cache operations

## Output

- Operation results

## Example

```text
LRUCache(2)
put(1,1), put(2,2), get(1) -> 1
put(3,3) evicts key 2
get(2) -> -1
```

## Intuition

Use a hash map for key lookup and a doubly linked list for recency order. Move accessed nodes to the front.

## Solution

```python
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.left = Node()
        self.right = Node()
        self.left.next = self.right
        self.right.prev = self.left

    def _remove(self, node):
        prev_node, next_node = node.prev, node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _insert_recent(self, node):
        prev_node = self.right.prev
        prev_node.next = node
        node.prev = prev_node
        node.next = self.right
        self.right.prev = node

    def get(self, key):
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self._remove(node)
        self._insert_recent(node)
        return node.value

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])

        node = Node(key, value)
        self.cache[key] = node
        self._insert_recent(node)

        if len(self.cache) > self.capacity:
            lru = self.left.next
            self._remove(lru)
            del self.cache[lru.key]
```

## Complexity

- Time: `O(1)` average per operation
- Space: `O(capacity)`

