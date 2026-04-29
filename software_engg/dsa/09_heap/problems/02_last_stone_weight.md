# Last Stone Weight

## Question

You are given an array of integers `stones` where `stones[i]` is the weight of the ith stone.

We are playing a game with the stones. On each turn, we choose the **heaviest two stones** and smash them together. Suppose the stones have weights `x` and `y` with `x <= y`. The result of this smash is:

- If `x == y`, both stones are destroyed
- If `x != y`, the stone of weight `x` is destroyed, and the stone of weight `y` has new weight `y - x`

At the end of the game, there is **at most one stone left**.

Return the weight of the last remaining stone. If there are no stones left, return `0`.

## Examples

### Example 1
```
Input: stones = [2,7,4,1,8,1]
Output: 1
Explanation:
- Smash 8 and 7 → result is 1, array becomes [2,4,1,1,1]
- Smash 4 and 2 → result is 2, array becomes [2,1,1,1]
- Smash 2 and 1 → result is 1, array becomes [1,1,1]
- Smash 1 and 1 → both destroyed, array becomes [1]
- Return 1
```

### Example 2
```
Input: stones = [1]
Output: 1
```

### Example 3
```
Input: stones = [1,1]
Output: 0
```

## Constraints

- `1 <= stones.length <= 30`
- `1 <= stones[i] <= 1000`

## Solution Approaches

### Approach 1: Max-Heap (Using Negation)
```python
import heapq

def lastStoneWeight(stones):
    # Python has min-heap, so negate values for max-heap
    heap = [-stone for stone in stones]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        # Pop two heaviest stones
        stone1 = heapq.heappop(heap)
        stone2 = heapq.heappop(heap)
        
        # If not equal, push the difference back
        if stone1 != stone2:
            heapq.heappush(heap, stone1 - stone2)
    
    return -heap[0] if heap else 0
```

### Approach 2: Simulation with Sorting
```python
def lastStoneWeight(stones):
    while len(stones) > 1:
        stones.sort(reverse=True)
        y = stones.pop(0)  # Heaviest
        x = stones.pop(0)  # Second heaviest
        
        if x != y:
            stones.append(y - x)
    
    return stones[0] if stones else 0
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Max-Heap | O(n log n) | O(n) |
| Sorting | O(n² log n) | O(1) |

Where n = number of stones

## Key Insights

- **Max-heap**: Always access heaviest stones efficiently
- **Negation trick**: Python's heapq is min-heap, negate for max-heap
- **Smash logic**: Difference goes back to heap if not equal

## Visual Explanation

```
stones = [2,7,4,1,8,1]

Max-heap (negated): [-8, -7, -4, -2, -1, -1]

Step 1: Pop -8 and -7
        8 != 7, push -(8-7) = -1
        Heap: [-4, -2, -1, -1, -1]

Step 2: Pop -4 and -2
        4 != 2, push -(4-2) = -2
        Heap: [-2, -1, -1, -1]

Step 3: Pop -2 and -1
        2 != 1, push -(2-1) = -1
        Heap: [-1, -1, -1]

Step 4: Pop -1 and -1
        1 == 1, both destroyed
        Heap: [-1]

Return 1
```

## Algorithm Steps

1. Build max-heap (negate values for Python)
2. While more than 1 stone:
   - Pop two heaviest stones
   - If different weights, push difference back
   - If equal, both destroyed (do nothing)
3. Return remaining stone weight or 0

## Why Heap?

- Efficiently get two heaviest stones: O(log n)
- Insert difference back: O(log n)
- Total: O(n log n) vs O(n² log n) for sorting

## Related Problems

- [Kth Largest Element in a Stream](problems/01_kth_largest_stream.md)
- [Top K Frequent Elements](problems/05_top_k_frequent.md)
- [K Closest Points to Origin](problems/03_k_closest_points.md)