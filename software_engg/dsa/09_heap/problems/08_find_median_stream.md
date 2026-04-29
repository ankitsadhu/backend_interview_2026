# Find Median from Data Stream

## Question

The **median** is the middle value in an ordered integer list. If the size of the list is even, there is no middle value and the median is the mean of the two middle values.

- For example, for `arr = [2,3,4]`, the median is `3`.
- For example, for `arr = [2,3]`, the median is `(2 + 3) / 2 = 2.5`.

Implement the `MedianFinder` class:

- `MedianFinder()` - Initializes the `MedianFinder` object.
- `void addNum(int num)` - Adds the integer `num` from the data stream to the data structure.
- `double findMedian()` - Returns the median of all elements so far.

## Examples

### Example 1
```
Input
["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"]
[[], [1], [2], [], [3], []]

Output
[null, null, null, 1.5, null, 2.0]

Explanation
MedianFinder medianFinder = new MedianFinder();
medianFinder.addNum(1);    // arr = [1]
medianFinder.addNum(2);    // arr = [1, 2]
medianFinder.findMedian(); // return 1.5 (i.e., (1 + 2) / 2)
medianFinder.addNum(3);    // arr = [1, 2, 3]
medianFinder.findMedian(); // return 2.0
```

## Constraints

- `-10^5 <= num <= 10^5`
- There will be at least one element in the data structure before calling `findMedian`.
- At most `5 * 10^4` calls will be made to `addNum` and `findMedian`.

## Follow-up

1. If all integer numbers from the stream are in the range `[0, 100]`, how would you optimize your solution?
2. If `99%` of all integer numbers from the stream are in the range `[0, 100]`, how would you optimize your solution?

## Solution Approaches

### Approach: Two Heaps (Optimal)
```python
import heapq

class MedianFinder:
    def __init__(self):
        # Max-heap for smaller half (negate values)
        self.small = []
        # Min-heap for larger half
        self.large = []
    
    def addNum(self, num: int) -> None:
        # Add to appropriate heap
        if not self.small or num <= -self.small[0]:
            heapq.heappush(self.small, -num)
        else:
            heapq.heappush(self.large, num)
        
        # Balance heaps
        if len(self.small) > len(self.large) + 1:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        elif len(self.large) > len(self.small):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)
    
    def findMedian(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        else:
            return (-self.small[0] + self.large[0]) / 2.0
```

## Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| addNum | O(log n) | O(n) |
| findMedian | O(1) | O(1) |

Where n = number of elements

## Key Insights

- **Two heaps**: 
  - Max-heap (`small`) for smaller half (negate values for max-heap behavior in Python)
  - Min-heap (`large`) for larger half
- **Balance**: Size difference should be at most 1
- **Median calculation**:
  - Odd size: Top of larger heap
  - Even size: Average of both heap tops

## Visual Explanation

```
Adding 1:
small: [-1], large: []
Median: 1

Adding 2:
small: [-1], large: [2]
Median: (1 + 2) / 2 = 1.5

Adding 3:
Balance: Move 2 to small, add 3 to large
small: [-2, -1], large: [3]
Median: 2
```

## Algorithm Steps

1. **Add number**:
   - If number <= max of small half → add to small heap
   - Else → add to large heap
2. **Balance heaps**:
   - If small size > large size + 1 → move from small to large
   - If large size > small size → move from large to small
3. **Find median**:
   - If small has more elements → small top is median
   - Else → average of small top and large top

## Follow-up Answers

1. **Range [0, 100]**: Use frequency array of size 101
2. **99% in [0, 100]**: Use frequency array + list for outliers

## Related Problems

- [Sliding Window Median](problems/09_sliding_window_median.md)
- [Kth Largest Element in a Stream](problems/01_kth_largest_stream.md)
- [Top K Frequent Elements](problems/05_top_k_frequent.md)