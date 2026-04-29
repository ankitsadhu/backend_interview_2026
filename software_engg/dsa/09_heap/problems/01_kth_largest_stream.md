# Kth Largest Element in a Stream

## Question

Design a class to find the **kth largest element** in a stream. Note that it is the kth largest element in the sorted order, not the kth distinct element.

Implement the `KthLargest` class:
- `KthLargest(int k, int[] nums)` - Initializes the object with the integer k and the stream of integers nums.
- `int add(int val)` - Appends the integer val to the stream and returns the element representing the kth largest element in the stream.

## Examples

### Example 1
```
Input
["KthLargest", "add", "add", "add", "add", "add"]
[[3, [4, 5, 8, 2]], [3], [5], [10], [9], [4]]

Output
[null, 4, 5, 5, 8, 8]

Explanation
KthLargest kthLargest = new KthLargest(3, [4, 5, 8, 2]);
kthLargest.add(3);   // return 4 (stream: [2, 3, 4, 5, 8])
kthLargest.add(5);   // return 5 (stream: [2, 3, 4, 5, 5, 8])
kthLargest.add(10);  // return 5 (stream: [2, 3, 4, 5, 5, 8, 10])
kthLargest.add(9);   // return 8 (stream: [2, 3, 4, 5, 5, 8, 9, 10])
kthLargest.add(4);   // return 8 (stream: [2, 3, 4, 4, 5, 5, 8, 9, 10])
```

## Constraints

- `1 <= k <= 10^4`
- `0 <= nums.length <= 10^4`
- `-10^4 <= nums[i] <= 10^4`
- `-10^4 <= val <= 10^4`
- At most `10^4` calls will be made to `add`.

## Solution Approaches

### Approach 1: Min-Heap of Size K (Optimal)
```python
import heapq

class KthLargest:
    def __init__(self, k: int, nums: List[int]):
        self.k = k
        self.heap = []
        
        # Build min-heap with at most k elements
        for num in nums:
            self.add(num)
    
    def add(self, val: int) -> int:
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:
            heapq.heapreplace(self.heap, val)
        
        return self.heap[0]
```

### Approach 2: Max-Heap (Less Efficient)
```python
import heapq

class KthLargest:
    def __init__(self, k: int, nums: List[int]):
        self.k = k
        # Negate values for max-heap
        self.heap = [-num for num in nums]
        heapq.heapify(self.heap)
    
    def add(self, val: int) -> int:
        heapq.heappush(self.heap, -val)
        
        # Remove elements until we have k largest
        while len(self.heap) > self.k:
            heapq.heappop(self.heap)
        
        return -self.heap[0]
```

## Complexity Analysis

| Approach | __init__ Time | add Time | Space |
|----------|---------------|----------|-------|
| Min-Heap | O(n log k) | O(log k) | O(k) |
| Max-Heap | O(n) | O(n log n) | O(n) |

Where n = initial array size

## Key Insights

- **Min-heap of size k**: Root is the kth largest element
- **Keep only k largest**: Discard smaller elements
- **O(1) query**: Root always has the answer

## Visual Explanation

```
k = 3, nums = [4, 5, 8, 2]

Initial heap (min-heap of size 3):
    4
   / \
  5   8

add(3): 3 < 4, so don't add. Return 4
add(5): 5 > 4, replace 4 with 5
    5
   / \
  5   8
Return 5

add(10): 10 > 5, replace 5 with 10
    5
   / \
  8   10
Return 5

add(9): 9 > 5, replace 5 with 9
    8
   / \
  9   10
Return 8
```

## Algorithm Steps

1. **Initialization**: Build min-heap with at most k largest elements
2. **Add operation**:
   - If heap size < k: push new element
   - If new element > heap root: replace root
   - Otherwise: ignore (element is not in top k)
3. **Return**: Root of min-heap (kth largest)

## Why Min-Heap?

- Min-heap keeps smallest of the k largest at root
- Root is exactly the kth largest element
- O(log k) for add operation

## Related Problems

- [Kth Largest Element in an Array](problems/04_kth_largest_array.md)
- [Find Median from Data Stream](problems/08_find_median_stream.md)
- [Top K Frequent Elements](problems/05_top_k_frequent.md)