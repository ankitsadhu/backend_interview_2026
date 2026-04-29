# All O`one Data Structure

## Problem

Design a data structure that supports `inc`, `dec`, `getMaxKey`, and `getMinKey` in `O(1)` average time.

## Input

- Operations on keys

## Output

- Operation results

## Example

```text
inc("hello")
inc("hello")
getMaxKey() -> "hello"
getMinKey() -> "hello"
```

## Intuition

Group keys by count in doubly linked buckets. Each key points to its current bucket, so increment/decrement can move it to a neighboring bucket.

## Solution

```python
class Bucket:
    def __init__(self, count):
        self.count = count
        self.keys = set()
        self.prev = None
        self.next = None

class AllOne:
    def __init__(self):
        self.key_to_bucket = {}
        self.head = Bucket(0)
        self.tail = Bucket(0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _insert_after(self, node, new_node):
        nxt = node.next
        node.next = new_node
        new_node.prev = node
        new_node.next = nxt
        nxt.prev = new_node

    def _remove_bucket(self, bucket):
        bucket.prev.next = bucket.next
        bucket.next.prev = bucket.prev

    def inc(self, key):
        if key not in self.key_to_bucket:
            first = self.head.next
            if first == self.tail or first.count != 1:
                first = Bucket(1)
                self._insert_after(self.head, first)
            first.keys.add(key)
            self.key_to_bucket[key] = first
            return

        bucket = self.key_to_bucket[key]
        next_count = bucket.count + 1
        nxt = bucket.next
        if nxt == self.tail or nxt.count != next_count:
            nxt = Bucket(next_count)
            self._insert_after(bucket, nxt)

        bucket.keys.remove(key)
        nxt.keys.add(key)
        self.key_to_bucket[key] = nxt
        if not bucket.keys:
            self._remove_bucket(bucket)

    def dec(self, key):
        bucket = self.key_to_bucket[key]
        bucket.keys.remove(key)

        if bucket.count == 1:
            del self.key_to_bucket[key]
        else:
            prev_count = bucket.count - 1
            prev = bucket.prev
            if prev == self.head or prev.count != prev_count:
                prev = Bucket(prev_count)
                self._insert_after(bucket.prev, prev)
            prev.keys.add(key)
            self.key_to_bucket[key] = prev

        if not bucket.keys:
            self._remove_bucket(bucket)

    def getMaxKey(self):
        if self.tail.prev == self.head:
            return ""
        return next(iter(self.tail.prev.keys))

    def getMinKey(self):
        if self.head.next == self.tail:
            return ""
        return next(iter(self.head.next.keys))
```

## Complexity

- Time: `O(1)` average per operation
- Space: `O(n)`

