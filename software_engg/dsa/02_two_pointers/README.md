# Two Pointers

Solve these in order. The sequence starts with basic left/right pointers, then moves into in-place write pointers, sorted pair-sum patterns, greedy two pointers, intervals, and sliding-window style pointer problems.

## 1. Basic Left/Right Pointers

| Order | Problem | Why solve now? |
|---:|---|---|
| 1 | [Reverse String](problems/01_reverse_string.md) | Simplest two-pointer swap pattern. |
| 2 | [Valid Palindrome](problems/02_valid_palindrome.md) | Skip irrelevant characters while moving inward. |
| 3 | [Valid Palindrome II](problems/03_valid_palindrome_ii.md) | Try at most one deletion when pointers mismatch. |
| 4 | [Merge Strings Alternately](problems/04_merge_strings_alternately.md) | Two read pointers over two strings. |
| 5 | [Is Subsequence](problems/05_is_subsequence.md) | Matching one pointer only when characters align. |

## 2. In-Place Array Write Pointers

| Order | Problem | Why solve now? |
|---:|---|---|
| 6 | [Remove Element](problems/06_remove_element.md) | Basic slow/fast overwrite pattern. |
| 7 | [Remove Duplicates from Sorted Array](problems/07_remove_duplicates_sorted_array.md) | Keep one copy of each sorted value. |
| 8 | [Remove Duplicates from Sorted Array II](problems/08_remove_duplicates_sorted_array_ii.md) | Keep at most two copies. |
| 9 | [Move Zeroes](problems/09_move_zeroes.md) | Stable compaction plus fill/swap. |
| 10 | [Sort Colors](problems/10_sort_colors.md) | Three-way partition with low/mid/high pointers. |
| 11 | [Squares of a Sorted Array](problems/11_squares_of_sorted_array.md) | Fill output from the largest square backward. |

## 3. Sorted Pair and K-Sum

| Order | Problem | Why solve now? |
|---:|---|---|
| 12 | [Two Sum II - Input Array Is Sorted](problems/12_two_sum_ii_sorted.md) | Core sorted two-sum pattern. |
| 13 | [3Sum](problems/13_3sum.md) | Fix one value, then use two-sum. |
| 14 | [3Sum Closest](problems/14_3sum_closest.md) | Move pointers based on distance to target. |
| 15 | [4Sum](problems/15_4sum.md) | Generalize K-sum with duplicate skipping. |

## 4. Greedy Opposite-End Pointers

| Order | Problem | Why solve now? |
|---:|---|---|
| 16 | [Container With Most Water](problems/16_container_with_most_water.md) | Move the limiting side inward. |
| 17 | [Boats to Save People](problems/17_boats_to_save_people.md) | Pair lightest and heaviest greedily. |
| 18 | [Trapping Rain Water](problems/18_trapping_rain_water.md) | Maintain left/right max while moving inward. |

## 5. Intervals and Window-Style Pointers

| Order | Problem | Why solve now? |
|---:|---|---|
| 19 | [Interval List Intersections](problems/19_interval_list_intersections.md) | Advance the interval that ends first. |
| 20 | [Max Consecutive Ones III](problems/20_max_consecutive_ones_iii.md) | Sliding window using two boundary pointers. |

## Problems Added

The original list covered the main interview set. I added these bridge problems:

- Valid Palindrome
- Valid Palindrome II
- Sort Colors

They make pointer movement, mismatch handling, and partitioning easier before the harder sum and water problems.
