# Kth Largest Element in an Array

## Question

Given an integer array `nums` and an integer `k`, return the **kth largest element** in the array.

Note that it is the kth largest element in the sorted order, not the kth distinct element.

## Examples

### Example 1
```
Input: nums = [3,2,1,5,6,4], k = 2
Output: 5
Explanation: Sorted array: [1, 2, 3, 4, 5, 6]. 2nd largest is 5.
```

### Example 2
```
Input: nums = [3,2,3,1,2,4,5,5,6], k = 4
Output: 4
Explanation: Sorted array: [1, 2, 2, 3, 3, 4, 5, 5, 6]. 4th largest is 4.
```

### Example 3
```
Input: nums = [1], k = 1
Output: 1
```

## Constraints

- `1 <= k <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`

## Solution Approaches

### Approach 1: Min-Heap of Size K
```python
import heapq

def findKthLargest(nums, k):
    # Min-heap of size k
    heap = []
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heapreplace(heap, num)
    
    return heap[0]
```

### Approach 2: Quick Select (Average O(n))
```python
import random

def findKthLargest(nums, k):
    k = len(nums) - k  # Convert kth largest to index
    
    def partition(left, right, pivot_idx):
        pivot = nums[pivot_idx]
        # Move pivot to end
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]
        
        store_idx = left
        for i in range(left, right):
            if nums[i] < pivot:
                nums[store_idx], nums[i] = nums[i], nums[store_idx]
                store_idx += 1
        
        # Move pivot to its final place
        nums[right], nums[store_idx] = nums[store_idx], nums[right]
        return store_idx
    
    def select(left, right):
        if left == right:
            return nums[left]
        
        pivot_idx = random.randint(left, right)
        pivot_idx = partition(left, right, pivot_idx)
        
        if k == pivot_idx:
            return nums[k]
        elif k < pivot_idx:
            return select(left, pivot_idx - 1)
        else:
            return select(pivot_idx + 1, right)
    
    return select(0, len(nums) - 1)
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Min-Heap | O(n log k) | O(k) |
| Quick Select | O(n) average, O(n²) worst | O(1) |

Where n = number of elements

## Key Insights

- **Min-heap**: Keep k largest elements, root is kth largest
- **Quick select**: Partition to find kth largest
- **Tradeoff**: Quick select average O(n), heap worst O(n log k)

## Visual Explanation

```
nums = [3,2,1,5,6,4], k = 2

Min-heap approach:
1. Add 3 → heap: [3]
2. Add 2 → heap: [2, 3] (size = k = 2)
3. 1 < 2 → skip
4. 5 > 2 → replace → heap: [3, 5]
5. 6 > 3 → replace → heap: [5, 6]
6. 4 < 5 → skip

Return heap[0] = 5
```

## Algorithm Steps (Heap)

1. Initialize min-heap
2. Iterate through all numbers:
   - If heap size < k: push number
   - If number > heap root: replace root
3. Return heap root (kth largest)

## Related Problems

- [Kth Largest Element in a Stream](problems/01_kth_largest_stream.md)
- [Top K Frequent Elements](problems/05_top_k_frequent.md)
- [K Closest Points to Origin](problems/03_k_closest_points.md)