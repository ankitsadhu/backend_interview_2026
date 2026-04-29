# Array and Hashing

Solve these in order. The sequence starts with array traversal and in-place basics, then moves into hash maps/sets, prefix sums, Kadane-style DP, greedy array problems, and matrix simulation.

## 1. Array Fundamentals

| Order | Problem | Why solve now? |
|---:|---|---|
| 1 | [Running Sum of 1D Array](problems/01_running_sum_1d_array.md) | Warm up with linear traversal. |
| 2 | [Rotate Array](problems/02_rotate_array.md) | Learn in-place index manipulation. |
| 3 | [Find All Numbers Disappeared in an Array](problems/03_find_all_numbers_disappeared_in_array.md) | Use array indices as markers. |
| 4 | [First Missing Positive](problems/04_first_missing_positive.md) | Hard in-place placement pattern. |
| 5 | [Contains Duplicate](problems/05_contains_duplicate.md) | First hash set problem. |
| 6 | [Missing Number](problems/06_missing_number.md) | Common XOR/sum interview warmup. |

## 2. Hash Maps and Frequency

| Order | Problem | Why solve now? |
|---:|---|---|
| 7 | [Valid Anagram](problems/07_valid_anagram.md) | Frequency counting. |
| 8 | [Two Sum](problems/08_two_sum.md) | Hash map lookup while scanning. |
| 9 | [Group Anagrams](problems/09_group_anagrams.md) | Hashable signatures. |
| 10 | [Top K Frequent Elements](problems/10_top_k_frequent_elements.md) | Frequency map plus heap/bucket sort. |
| 11 | [Intersection of Two Arrays](problems/11_intersection_of_two_arrays.md) | Set intersection. |
| 12 | [Intersection of Two Arrays II](problems/12_intersection_of_two_arrays_ii.md) | Count-aware intersection. |
| 13 | [Majority Element](problems/13_majority_element.md) | Boyer-Moore voting. |
| 14 | [Majority Element II](problems/14_majority_element_ii.md) | Extended Boyer-Moore. |
| 15 | [4Sum II](problems/15_4sum_ii.md) | Pair-sum frequency map. |
| 16 | [Bulls and Cows](problems/16_bulls_and_cows.md) | Frequency difference while matching. |

## 3. Encoding, Design, and Hash Set Patterns

| Order | Problem | Why solve now? |
|---:|---|---|
| 17 | [Encode and Decode Strings](problems/17_encode_decode_strings.md) | Design a reversible string format. |
| 18 | [Insert Delete GetRandom O(1)](problems/18_insert_delete_getrandom_o1.md) | Combine array and hash map for O(1) operations. |
| 19 | [Longest Consecutive Sequence](problems/19_longest_consecutive_sequence.md) | Hash set sequence starts. |
| 20 | [Product of Array Except Self](problems/20_product_array_except_self.md) | Prefix/suffix product without division. |

## 4. Prefix Sum and Remainder Hashing

| Order | Problem | Why solve now? |
|---:|---|---|
| 21 | [Subarray Sum Equals K](problems/21_subarray_sum_equals_k.md) | Core prefix-sum frequency template. |
| 22 | [Continuous Subarray Sum](problems/22_continuous_subarray_sum.md) | Prefix remainder map. |
| 23 | [Contiguous Array](problems/23_contiguous_array.md) | Transform binary array into prefix balance. |
| 24 | [Subarray Sums Divisible by K](problems/24_subarray_sums_divisible_by_k.md) | Count equal prefix remainders. |

## 5. Kadane and Greedy Arrays

| Order | Problem | Why solve now? |
|---:|---|---|
| 25 | [Maximum Subarray](problems/25_maximum_subarray.md) | Classic Kadane's algorithm. |
| 26 | [Maximum Product Subarray](problems/26_maximum_product_subarray.md) | Track both max and min products. |
| 27 | [Best Time to Buy and Sell Stock](problems/27_best_time_to_buy_sell_stock.md) | One-pass min price pattern. |
| 28 | [Gas Station](problems/28_gas_station.md) | Greedy reset pattern. |
| 29 | [Candy](problems/29_candy.md) | Two-pass greedy constraints. |

## 6. Matrix and Simulation

| Order | Problem | Why solve now? |
|---:|---|---|
| 30 | [Valid Sudoku](problems/30_valid_sudoku.md) | Hash sets over rows, columns, and boxes. |
| 31 | [Rotate Image](problems/31_rotate_image.md) | In-place matrix transform. |
| 32 | [Set Matrix Zeroes](problems/32_set_matrix_zeroes.md) | Use first row/column as markers. |
| 33 | [Spiral Matrix](problems/33_spiral_matrix.md) | Boundary simulation. |
| 34 | [Spiral Matrix II](problems/34_spiral_matrix_ii.md) | Fill a matrix using boundary simulation. |
| 35 | [Game of Life](problems/35_game_of_life.md) | In-place state encoding. |

## Problems Added

The original list already covered the major NeetCode-style array/hash set. I added these bridge problems because they are common interview stepping stones:

- Running Sum of 1D Array
- Missing Number
- Best Time to Buy and Sell Stock

They make prefix sums, XOR/sum reasoning, and one-pass array state easier before the harder variants.
