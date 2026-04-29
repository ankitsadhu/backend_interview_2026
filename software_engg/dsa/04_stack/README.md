# Stack

Solve these in order. The sequence starts with basic LIFO usage, then moves into encoded strings and calculators, monotonic stacks, and advanced histogram/counting patterns.

## 1. Basic Stack Patterns

| Order | Problem | Why solve now? |
|---:|---|---|
| 1 | [Valid Parentheses](problems/01_valid_parentheses.md) | Core matching stack pattern. |
| 2 | [Baseball Game](problems/02_baseball_game.md) | Stack as operation history. |
| 3 | [Backspace String Compare](problems/03_backspace_string_compare.md) | Stack simulation for editing. |
| 4 | [Min Stack](problems/04_min_stack.md) | Stack with auxiliary state. |
| 5 | [Evaluate Reverse Polish Notation](problems/05_evaluate_reverse_polish_notation.md) | Stack for expression evaluation. |
| 6 | [Simplify Path](problems/06_simplify_path.md) | Stack for filesystem path normalization. |
| 7 | [Asteroid Collision](problems/07_asteroid_collision.md) | Stack for resolving previous active elements. |

## 2. Nested and Expression Parsing

| Order | Problem | Why solve now? |
|---:|---|---|
| 8 | [Generate Parentheses](problems/08_generate_parentheses.md) | Backtracking with stack-like balance. |
| 9 | [Decode String](problems/09_decode_string.md) | Stack for nested repeat expressions. |
| 10 | [Basic Calculator II](problems/10_basic_calculator_ii.md) | Operator precedence using a stack. |
| 11 | [Basic Calculator](problems/11_basic_calculator.md) | Parentheses and sign context. |
| 12 | [Longest Valid Parentheses](problems/12_longest_valid_parentheses.md) | Stack of indices for valid ranges. |

## 3. Monotonic Stack

| Order | Problem | Why solve now? |
|---:|---|---|
| 13 | [Next Greater Element I](problems/13_next_greater_element_i.md) | First decreasing-stack mapping. |
| 14 | [Next Greater Element II](problems/14_next_greater_element_ii.md) | Circular next-greater pattern. |
| 15 | [Daily Temperatures](problems/15_daily_temperatures.md) | Distance to next greater value. |
| 16 | [Online Stock Span](problems/16_online_stock_span.md) | Monotonic stack as an online data structure. |
| 17 | [Next Greater Node in Linked List](problems/17_next_greater_node_linked_list.md) | Apply monotonic stack after traversal. |
| 18 | [Car Fleet](problems/18_car_fleet.md) | Stack-like grouping after sorting. |

## 4. Monotonic Stack for Optimization

| Order | Problem | Why solve now? |
|---:|---|---|
| 19 | [Remove K Digits](problems/19_remove_k_digits.md) | Monotonic increasing stack for smallest number. |
| 20 | [Remove Duplicate Letters](problems/20_remove_duplicate_letters.md) | Monotonic stack with last occurrence constraints. |
| 21 | [Sum of Subarray Minimums](problems/21_sum_of_subarray_minimums.md) | Count contribution using previous/next smaller. |
| 22 | [Largest Rectangle in Histogram](problems/22_largest_rectangle_histogram.md) | Increasing stack for max rectangle. |
| 23 | [Maximal Rectangle](problems/23_maximal_rectangle.md) | Reduce each matrix row to histogram. |

## Problems Added

The original list already had the main stack interview problems. I added these bridge problems:

- Baseball Game
- Backspace String Compare
- Asteroid Collision

They make plain stack simulation and collision-style popping easier before the harder monotonic stack problems.
