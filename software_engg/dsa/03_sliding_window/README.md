# Sliding Window

Solve these in order. The sequence starts with fixed-size windows, then variable-size windows, frequency-map windows, deque windows, and advanced substring matching.

## 1. Fixed-Size Windows

| Order | Problem | Why solve now? |
|---:|---|---|
| 1 | [Maximum Average Subarray I](problems/01_maximum_average_subarray_i.md) | Simplest fixed-size sum window. |
| 2 | [Number of Sub-arrays of Size K and Average >= Threshold](problems/02_subarrays_size_k_average_threshold.md) | Same fixed-size sum with a condition. |
| 3 | [Maximum Number of Vowels in a Substring of Given Length](problems/03_maximum_vowels_substring_length_k.md) | Fixed-size window over characters. |
| 4 | [Grumpy Bookstore Owner](problems/04_grumpy_bookstore_owner.md) | Fixed-size window for maximum extra gain. |

## 2. Variable-Size Windows

| Order | Problem | Why solve now? |
|---:|---|---|
| 5 | [Best Time to Buy and Sell Stock](problems/05_best_time_to_buy_sell_stock.md) | One-pass window/state warmup. |
| 6 | [Minimum Size Subarray Sum](problems/06_minimum_size_subarray_sum.md) | Shrink while the window is valid. |
| 7 | [Max Consecutive Ones III](problems/07_max_consecutive_ones_iii.md) | Longest valid window with at most `k` bad values. |
| 8 | [Longest Substring Without Repeating Characters](problems/08_longest_substring_without_repeating.md) | Shrink to remove duplicates. |

## 3. Distinct Character Windows

| Order | Problem | Why solve now? |
|---:|---|---|
| 9 | [Fruit Into Baskets](problems/09_fruit_into_baskets.md) | Longest window with at most two distinct values. |
| 10 | [Longest Substring with At Most Two Distinct Characters](problems/10_longest_substring_at_most_two_distinct.md) | Character version of at-most-two distinct. |
| 11 | [Longest Substring with At Most K Distinct Characters](problems/11_longest_substring_at_most_k_distinct.md) | General distinct-count template. |
| 12 | [Longest Repeating Character Replacement](problems/12_longest_repeating_character_replacement.md) | Keep window valid using max frequency. |

## 4. Frequency Matching Windows

| Order | Problem | Why solve now? |
|---:|---|---|
| 13 | [Permutation in String](problems/13_permutation_in_string.md) | Fixed-size frequency comparison. |
| 14 | [Find All Anagrams in a String](problems/14_find_all_anagrams_in_string.md) | Return every matching frequency window. |
| 15 | [Minimum Window Substring](problems/15_minimum_window_substring.md) | Minimum valid covering window. |

## 5. Deque and Advanced Windows

| Order | Problem | Why solve now? |
|---:|---|---|
| 16 | [Sliding Window Maximum](problems/16_sliding_window_maximum.md) | Monotonic deque for max in each window. |
| 17 | [Minimum Number of K Consecutive Bit Flips](problems/17_minimum_k_consecutive_bit_flips.md) | Track active flips over a moving window. |
| 18 | [Substring with Concatenation of All Words](problems/18_substring_with_concatenation_all_words.md) | Advanced fixed-word window with frequency counts. |

## Problems Added

The original list already covered many strong sliding-window problems. I added these bridge problems:

- Maximum Average Subarray I
- Max Consecutive Ones III
- Fruit Into Baskets

They make fixed-size windows, at-most-`k` invalid windows, and at-most-distinct windows easier before harder variants.
