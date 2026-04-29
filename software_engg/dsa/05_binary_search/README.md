# Binary Search

Solve these in order. The sequence starts with exact search and boundaries, then moves into rotated arrays, matrix/peak problems, binary search on answer, and advanced sorted-array problems.

## 1. Basic Binary Search and Boundaries

| Order | Problem | Why solve now? |
|---:|---|---|
| 1 | [Binary Search](problems/01_binary_search.md) | Core `left <= right` exact search. |
| 2 | [Search Insert Position](problems/02_search_insert_position.md) | First lower-bound style problem. |
| 3 | [Lower Bound and Upper Bound](problems/03_lower_bound_upper_bound.md) | Learn reusable boundary templates. |
| 4 | [Find First and Last Position of Element in Sorted Array](problems/04_find_first_last_position.md) | Apply lower/upper bounds to a range. |
| 5 | [Sqrt(x)](problems/05_sqrt_x.md) | Binary search over numeric answer. |
| 6 | [Valid Perfect Square](problems/06_valid_perfect_square.md) | Exact numeric binary search without floating point. |
| 7 | [First Bad Version](problems/07_first_bad_version.md) | First true in a boolean search space. |
| 8 | [Guess Number Higher or Lower](problems/08_guess_number_higher_lower.md) | Interactive-style exact search. |

## 2. Rotated Sorted Arrays

| Order | Problem | Why solve now? |
|---:|---|---|
| 9 | [Find Minimum in Rotated Sorted Array](problems/09_find_min_rotated_sorted_array.md) | Locate pivot/minimum without duplicates. |
| 10 | [Search in Rotated Sorted Array](problems/10_search_rotated_sorted_array.md) | Search by detecting the sorted half. |
| 11 | [Find Minimum in Rotated Sorted Array II](problems/11_find_min_rotated_sorted_array_ii.md) | Handle duplicate ambiguity. |
| 12 | [Search in Rotated Sorted Array II](problems/12_search_rotated_sorted_array_ii.md) | Rotated search with duplicates. |

## 3. Matrix, Peak, and Special Sorted Arrays

| Order | Problem | Why solve now? |
|---:|---|---|
| 13 | [Search a 2D Matrix](problems/13_search_2d_matrix.md) | Treat a matrix as a flattened sorted array. |
| 14 | [Find Peak Element](problems/14_find_peak_element.md) | Binary search using slope direction. |
| 15 | [Single Element in a Sorted Array](problems/15_single_element_sorted_array.md) | Parity-based binary search. |
| 16 | [Missing Positive Number in Sorted Array](problems/16_missing_positive_sorted_array.md) | Boundary search using missing-count function. |

## 4. Binary Search on Answer

| Order | Problem | Why solve now? |
|---:|---|---|
| 17 | [Koko Eating Bananas](problems/17_koko_eating_bananas.md) | Minimum feasible speed. |
| 18 | [Capacity To Ship Packages Within D Days](problems/18_capacity_ship_packages_d_days.md) | Minimum feasible capacity. |
| 19 | [Find the Smallest Divisor Given a Threshold](problems/19_smallest_divisor_threshold.md) | Minimum feasible divisor. |
| 20 | [Split Array Largest Sum](problems/20_split_array_largest_sum.md) | Minimize largest partition sum. |
| 21 | [Divide Chocolate](problems/21_divide_chocolate.md) | Maximize minimum sweetness. |

## 5. Advanced Sorted-Array Search

| Order | Problem | Why solve now? |
|---:|---|---|
| 22 | [Time Based Key-Value Store](problems/22_time_based_key_value_store.md) | Binary search over timestamped values. |
| 23 | [Find K Closest Elements](problems/23_find_k_closest_elements.md) | Binary search the left boundary of the answer window. |
| 24 | [Median of Two Sorted Arrays](problems/24_median_two_sorted_arrays.md) | Hard partition-based binary search. |

## Problems Added

The original list covered the main binary-search interview set. I added these bridge problems:

- Lower Bound and Upper Bound
- Missing Positive Number in Sorted Array

They make boundary thinking more explicit before harder rotated-array and partition-style problems.
