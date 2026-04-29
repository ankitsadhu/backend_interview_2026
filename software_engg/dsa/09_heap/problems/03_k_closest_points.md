# K Closest Points to Origin

## Question

Given an array of `points` where `points[i] = [xi, yi]` represents a point on the **X-Y** plane and an integer `k`, return the `k` closest points to the origin `(0, 0)`.

The distance between two points on the X-Y plane is the **Euclidean distance** (i.e., `√(x1 - x2)² + (y1 - y2)²`).

You may return the answer in **any order**. The answer is **guaranteed** to be **unique** (except for the order that it is in).

## Examples

### Example 1
```
Input: points = [[1,3],[-2,2]], k = 1
Output: [[-2,2]]
Explanation:
- Distance from (1,3) to origin: √(1² + 3²) = √10 ≈ 3.16
- Distance from (-2,2) to origin: √((-2)² + 2²) = √8 ≈ 2.83
- The closest point is (-2,2)
```

### Example 2
```
Input: points = [[3,3],[5,-1],[-2,4]], k = 2
Output: [[3,3],[-2,4]] or [[-2,4],[3,3]]
Explanation:
- Distance from (3,3): √18 ≈ 4.24
- Distance from (5,-1): √26 ≈ 5.10
- Distance from (-2,4): √20 ≈ 4.47
- Two closest: (3,3) and (-2,4)
```

### Example 3
```
Input: points = [[1,1],[2,2],[3,3],[4,4],[5,5]], k = 3
Output: [[1,1],[2,2],[3,3]]
```

## Constraints

- `1 <= k <= points.length <= 10^4`
- `-10^4 <= xi, yi <= 10^4`

## Solution Approaches

### Approach 1: Max-Heap of Size K
```python
import heapq

def kClosest(points, k):
    # Max-heap (negate distances)
    heap = []
    
    for x, y in points:
        # Use squared distance (no need for sqrt)
        dist = -(x * x + y * y)
        
        if len(heap) < k:
            heapq.heappush(heap, (dist, x, y))
        elif dist > heap[0][0]:  # If closer than farthest in heap
            heapq.heapreplace(heap, (dist, x, y))
    
    return [[x, y] for dist, x, y in heap]
```

### Approach 2: Quick Select (Average O(n))
```python
import random

def kClosest(points, k):
    def distance(point):
        return point[0] ** 2 + point[1] ** 2
    
    def partition(left, right, pivot_idx):
        pivot_dist = distance(points[pivot_idx])
        # Move pivot to end
        points[pivot_idx], points[right] = points[right], points[pivot_idx]
        store_idx = left
        
        for i in range(left, right):
            if distance(points[i]) < pivot_dist:
                points[store_idx], points[i] = points[i], points[store_idx]
                store_idx += 1
        
        # Move pivot to its final place
        points[right], points[store_idx] = points[store_idx], points[right]
        return store_idx
    
    def select(left, right, k_smallest):
        if left >= right:
            return
        
        # Random pivot
        pivot_idx = random.randint(left, right)
        pivot_idx = partition(left, right, pivot_idx)
        
        if k_smallest == pivot_idx:
            return
        elif k_smallest < pivot_idx:
            select(left, pivot_idx - 1, k_smallest)
        else:
            select(pivot_idx + 1, right, k_smallest)
    
    select(0, len(points) - 1, k)
    return points[:k]
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Max-Heap | O(n log k) | O(k) |
| Quick Select | O(n) average, O(n²) worst | O(1) |

Where n = number of points

## Key Insights

- **Max-heap**: Keep k closest points (smallest distances)
- **Squared distance**: Avoid expensive sqrt operation
- **Quick Select**: Partition around pivot like quicksort

## Visual Explanation

```
points = [[1,3],[-2,2]], k = 1

Distances (squared):
(1,3): 1² + 3² = 10
(-2,2): (-2)² + 2² = 8

Max-heap (size 1):
1. Add (1,3) with dist -10 → heap: [(-10, 1, 3)]
2. (-2,2) has dist -8 > -10, replace → heap: [(-8, -2, 2)]

Return [[-2, 2]]
```

## Algorithm Steps (Heap)

1. For each point, calculate squared distance
2. Use max-heap (negate distances) to keep k smallest
3. If heap size < k: push point
4. If point closer than heap max: replace
5. Return all points in heap

## Why Max-Heap?

- Max-heap root = farthest among k closest
- Easy to check if new point should be included
- O(log k) for each insertion/replacement

## Related Problems

- [Kth Largest Element in a Stream](problems/01_kth_largest_stream.md)
- [Top K Frequent Elements](problems/05_top_k_frequent.md)
- [Find K Pairs with Smallest Sums](problems/11_k_pairs_smallest_sums.md)