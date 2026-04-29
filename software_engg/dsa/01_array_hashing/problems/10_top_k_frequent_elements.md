# Top K Frequent Elements

## Problem

Given `nums` and integer `k`, return the `k` most frequent elements.

## Input

- `nums`: list of integers
- `k`: number of elements to return

## Output

- List of `k` frequent elements

## Example

```text
Input: nums = [1,1,1,2,2,3], k = 2
Output: [1,2]
```

## Intuition

Count frequencies, then use buckets where index means frequency.

## Solution

```python
from collections import Counter

def top_k_frequent(nums, k):
    count = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]

    for num, freq in count.items():
        buckets[freq].append(num)

    ans = []
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            ans.append(num)
            if len(ans) == k:
                return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

