# Top K Frequent Elements

## Question

Given an integer array `nums` and an integer `k`, return the `k` most frequent elements. You may return the answer in **any order**.

## Examples

### Example 1
```
Input: nums = [1,1,1,2,2,3], k = 2
Output: [1,2]
Explanation: 1 occurs 3 times, 2 occurs 2 times. Top 2 frequent elements.
```

### Example 2
```
Input: nums = [1], k = 1
Output: [1]
```

### Example 3
```
Input: nums = [4,1,-1,2,-1,2,3], k = 2
Output: [-1,2] or [2,-1]
```

## Constraints

- `1 <= nums.length <= 10^5`
- `-10^4 <= nums[i] <= 10^4`
- `k` is in the range `[1, number of unique elements in array]`
- It is **guaranteed** that the answer is **unique**.

## Follow-up

Your algorithm's time complexity must be **better** than **O(n log n)**, where n is the array's size.

## Solution Approaches

### Approach 1: Min-Heap of Size K
```python
import heapq
from collections import Counter

def topKFrequent(nums, k):
    # Count frequencies
    freq = Counter(nums)
    
    # Min-heap of size k
    heap = []
    for num, count in freq.items():
        if len(heap) < k:
            heapq.heappush(heap, (count, num))
        elif count > heap[0][0]:
            heapq.heapreplace(heap, (count, num))
    
    return [num for count, num in heap]
```

### Approach 2: Bucket Sort (O(n))
```python
from collections import Counter

def topKFrequent(nums, k):
    freq = Counter(nums)
    
    # Bucket sort by frequency
    bucket = [[] for _ in range(len(nums) + 1)]
    
    for num, count in freq.items():
        bucket[count].append(num)
    
    # Collect from highest frequency
    result = []
    for i in range(len(bucket) - 1, 0, -1):
        for num in bucket[i]:
            result.append(num)
            if len(result) == k:
                return result
    
    return result
```

### Approach 3: Quick Select
```python
import random
from collections import Counter

def topKFrequent(nums, k):
    freq = Counter(nums)
    unique = list(freq.keys())
    
    def partition(left, right, pivot_idx):
        pivot_count = freq[unique[pivot_idx]]
        # Move pivot to end
        unique[pivot_idx], unique[right] = unique[right], unique[pivot_idx]
        
        store_idx = left
        for i in range(left, right):
            if freq[unique[i]] < pivot_count:
                unique[store_idx], unique[i] = unique[i], unique[store_idx]
                store_idx += 1
        
        # Move pivot to its final place
        unique[right], unique[store_idx] = unique[store_idx], unique[right]
        return store_idx
    
    def select(left, right, k_smallest):
        if left == right:
            return
        
        pivot_idx = random.randint(left, right)
        pivot_idx = partition(left, right, pivot_idx)
        
        if k_smallest == pivot_idx:
            return
        elif k_smallest < pivot_idx:
            select(left, pivot_idx - 1, k_smallest)
        else:
            select(pivot_idx + 1, right, k_smallest)
    
    n = len(unique)
    select(0, n - 1, n - k)
    return unique[n - k:]
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Min-Heap | O(n log k) | O(n) |
| Bucket Sort | O(n) | O(n) |
| Quick Select | O(n) average, O(n²) worst | O(n) |

Where n = number of elements

## Key Insights

- **Hash Map + Heap**: Frequency map with min-heap of size k
- **Bucket Sort**: Group elements by frequency
- **Quick Select**: Partition to find top k elements

## Visual Explanation

```
nums = [1,1,1,2,2,3], k = 2

Frequency map:
1: 3
2: 2
3: 1

Min-heap (size 2):
1. Add (3, 1) → heap: [(3, 1)]
2. Add (2, 2) → heap: [(2, 2), (3, 1)]
3. 1 < 2 → skip

Result: [1, 2]
```

## Algorithm Steps (Heap)

1. Count frequencies using hash map (O(n))
2. Build min-heap of size k (O(n log k))
3. Return elements from heap

## Related Problems

- [Kth Largest Element in a Stream](problems/01_kth_largest_stream.md)
- [Kth Largest Element in an Array](problems/04_kth_largest_array.md)
- [Top K Frequent Words](problems/)
- [Sort Characters By Frequency](problems/)