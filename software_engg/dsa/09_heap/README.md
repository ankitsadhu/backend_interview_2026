# Heap/Priority Queue Problems

This directory contains comprehensive heap/priority queue problems organized by difficulty and pattern. Problems are arranged in a logical learning order from fundamentals to advanced concepts.

## Table of Contents

### 1. Basic Heap Operations (Foundation)
| # | Topic | Difficulty | Solution |
|---|-------|------------|----------|
| 1.1 | Kth Largest Element in a Stream | Easy | [Solution](problems/01_kth_largest_stream.md) |
| 1.2 | Last Stone Weight | Easy | [Solution](problems/02_last_stone_weight.md) |
| 1.3 | K Closest Points to Origin | Medium | [Solution](problems/03_k_closest_points.md) |
| 1.4 | Kth Largest Element in an Array | Medium | [Solution](problems/04_kth_largest_array.md) |

### 2. Heap with Hash Map
| # | Topic | Difficulty | Solution |
|---|-------|------------|----------|
| 2.1 | Top K Frequent Elements | Medium | [Solution](problems/05_top_k_frequent.md) |
| 2.2 | Task Scheduler | Medium | [Solution](problems/06_task_scheduler.md) |
| 2.3 | Design Twitter | Hard | [Solution](problems/07_design_twitter.md) |

### 3. Two Heaps Pattern
| # | Topic | Difficulty | Solution |
|---|-------|------------|----------|
| 3.1 | Find Median from Data Stream | Hard | [Solution](problems/08_find_median_stream.md) |
| 3.2 | Sliding Window Median | Hard | [Solution](problems/09_sliding_window_median.md) |

### 4. K-Way Merge Pattern
| # | Topic | Difficulty | Solution |
|---|-------|------------|----------|
| 4.1 | Kth Smallest Element in Sorted Matrix | Medium | [Solution](problems/10_kth_smallest_matrix.md) |
| 4.2 | Find K Pairs with Smallest Sums | Medium | [Solution](problems/11_k_pairs_smallest_sums.md) |
| 4.3 | Smallest Range Covering K Lists | Hard | [Solution](problems/12_smallest_range_k_lists.md) |
| 4.4 | K-th Smallest Prime Fraction | Hard | [Solution](problems/13_kth_smallest_prime.md) |

### 5. Top K Elements Pattern
| # | Topic | Difficulty | Solution |
|---|-------|------------|----------|
| 5.1 | IPO | Hard | [Solution](problems/14_ipo.md) |
| 5.2 | Furthest Building You Can Reach | Medium | [Solution](problems/15_furthest_building.md) |

### 6. Advanced Heap Problems
| # | Topic | Difficulty | Solution |
|---|-------|------------|----------|
| 6.1 | The Skyline Problem | Hard | [Solution](problems/16_skyline_problem.md) |
| 6.2 | Ugly Number II | Medium | [Solution](problems/17_ugly_number.md) |
| 6.3 | Super Ugly Number | Medium | [Solution](problems/18_super_ugly_number.md) |

## Common Heap Patterns

### 1. Kth Largest/Smallest
- Use **min-heap** for kth largest (keep k elements)
- Use **max-heap** for kth smallest (keep k elements)
- Time: O(n log k)

### 2. Top K Frequent
- Count frequencies with hash map
- Use heap to find top k
- Time: O(n log k)

### 3. Two Heaps (Median)
- Max-heap for smaller half
- Min-heap for larger half
- Balance heaps to find median

### 4. K-Way Merge
- Initialize heap with first element from each list
- Pop smallest, push next from same list
- Time: O(n log k) where k = number of lists

### 5. Interval/Range
- Sort intervals by start time
- Use heap to track active intervals
- Process events in order

## Key Concepts

- **Min-Heap**: Smallest element at root
- **Max-Heap**: Largest element at root
- **Heapify**: O(n) to build heap from array
- **Push/Pop**: O(log n) for single operation
- **Heap size**: Keep track of k for top-k problems

## Study Order

1. **Week 1**: Basic heap operations (problems 1-4)
2. **Week 2**: Heap with hash map (problems 5-7)
3. **Week 3**: Two heaps pattern (problems 8-9)
4. **Week 4**: K-way merge (problems 10-13)
5. **Week 5**: Advanced patterns (problems 14-18)

## Interview Tips

- **Identify the pattern**: Is it top-k, median, or merge?
- **Choose heap type**: Min-heap vs max-heap based on problem
- **Consider alternatives**: QuickSelect for kth element
- **Handle duplicates**: Use hash map with heap when needed
- **Balance tradeoffs**: Time vs space complexity

## Related Resources

- [Python heapq documentation](https://docs.python.org/3/library/heapq.html)
- [Java PriorityQueue](https://docs.oracle.com/javase/8/docs/api/java/util/PriorityQueue.html)
- [LeetCode Heap Explore](https://leetcode.com/explore/learn/card/heap/)