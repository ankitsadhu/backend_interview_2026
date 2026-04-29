# Recursion and Backtracking

Solve these in order. The sequence starts with plain recursion, then moves into choice diagrams, subsets/combinations, permutations, partitioning, grid search, and constraint solving.

## 1. Recursion Fundamentals

| Order | Problem | Why solve now? |
|---:|---|---|
| 1 | [Print Numbers Recursively](problems/01_print_numbers_recursively.md) | Learn base case and recursive call flow. |
| 2 | [Factorial](problems/02_factorial.md) | Classic single-branch recursion. |
| 3 | [Sum of Array](problems/03_sum_of_array.md) | Recursing over an index/range. |
| 4 | [Reverse String](problems/04_reverse_string.md) | Two-pointer recursion. |
| 5 | [Fibonacci Number](problems/05_fibonacci_number.md) | Shows overlapping subproblems and why memoization matters. |
| 6 | [pow(x, n)](problems/06_pow_x_n.md) | Divide-and-conquer recursion. |
| 7 | [3304. Find the K-th Character in String Game I](problems/07_kth_character_string_game_i.md) | Recursion from generated sequence patterns. |

## 2. Build Choice Diagrams

| Order | Problem | Why solve now? |
|---:|---|---|
| 8 | [Binary Strings Without Consecutive 1s](problems/08_binary_strings_without_consecutive_ones.md) | First clean include/exclude decision tree with constraints. |
| 9 | [Generate Parentheses](problems/09_generate_parentheses.md) | Backtracking with two counters and validity pruning. |
| 10 | [Letter Case Permutation](problems/10_letter_case_permutation.md) | Branch only when a character is alphabetic. |
| 11 | [Generalized Abbreviation](problems/11_generalized_abbreviation.md) | Track compact state while branching. |
| 12 | [Tower of Hanoi](problems/12_tower_of_hanoi.md) | Recursion where the subproblem definition is the whole trick. |

## 3. Subsets and Combinations

| Order | Problem | Why solve now? |
|---:|---|---|
| 13 | [Subsets](problems/13_subsets.md) | Core power-set template. |
| 14 | [Subsets II](problems/14_subsets_ii.md) | Same template with duplicate handling. |
| 15 | [Combinations](problems/15_combinations.md) | Choose `k` numbers from a range. |
| 16 | [Combination Sum](problems/16_combination_sum.md) | Reuse candidates while tracking remaining target. |
| 17 | [Combination Sum II](problems/17_combination_sum_ii.md) | No reuse plus duplicate skipping. |
| 18 | [Combination Sum III](problems/18_combination_sum_iii.md) | Fixed size and fixed sum. |
| 19 | [Find 3-Digit Even Numbers](problems/19_find_3_digit_even_numbers.md) | Small permutation/combination problem with digit constraints. |

## 4. Permutations

| Order | Problem | Why solve now? |
|---:|---|---|
| 20 | [Permutations](problems/20_permutations.md) | Core visited-array permutation template. |
| 21 | [Permutations II](problems/21_permutations_ii.md) | Duplicate-safe permutation generation. |
| 22 | [Letter Combinations of a Phone Number](problems/22_letter_combinations_phone_number.md) | Cartesian-product style recursion. |

## 5. Partitioning and String Backtracking

| Order | Problem | Why solve now? |
|---:|---|---|
| 23 | [Palindrome Partitioning](problems/23_palindrome_partitioning.md) | Choose cut positions and validate substrings. |
| 24 | [Restore IP Addresses](problems/24_restore_ip_addresses.md) | Partition with strict segment constraints. |
| 25 | [Maximum Length of a Concatenated String with Unique Characters](problems/25_max_unique_concat_string.md) | Subset recursion with a bitmask/state constraint. |

## 6. Grid and Constraint Backtracking

| Order | Problem | Why solve now? |
|---:|---|---|
| 26 | [Word Search](problems/26_word_search.md) | DFS with visited-state on a grid. |
| 27 | [Partition to K Equal Sum Subsets](problems/27_partition_to_k_equal_sum_subsets.md) | Bucket/backtracking pruning. |
| 28 | [N-Queens](problems/28_n_queens.md) | Constraint placement with columns and diagonals. |
| 29 | [N-Queens II](problems/29_n_queens_ii.md) | Count-only variant of N-Queens. |
| 30 | [Sudoku Solver](problems/30_sudoku_solver.md) | Full constraint satisfaction backtracking. |

## Problems Added

The original list jumped directly into harder backtracking. I added these bridge problems:

- Print Numbers Recursively
- Factorial
- Sum of Array
- Reverse String
- Fibonacci Number
- Binary Strings Without Consecutive 1s
- Tower of Hanoi

These make the later templates easier because they teach base cases, index movement, branching, pruning, and subproblem design separately.
