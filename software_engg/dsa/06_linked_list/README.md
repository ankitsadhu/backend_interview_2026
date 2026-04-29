# Linked List

Solve these in order. The sequence starts with basic node manipulation, then moves into fast/slow pointers, reversal patterns, merge/sort patterns, special pointer structures, and cache/data-structure design.

## 1. Linked List Basics

| Order | Problem | Why solve now? |
|---:|---|---|
| 1 | [Reverse Linked List](problems/01_reverse_linked_list.md) | Core pointer reversal pattern. |
| 2 | [Merge Two Sorted Lists](problems/02_merge_two_sorted_lists.md) | Dummy node and tail pointer basics. |
| 3 | [Delete Node in a Linked List](problems/03_delete_node_linked_list.md) | Local node mutation trick. |
| 4 | [Remove Duplicates from Sorted List](problems/04_remove_duplicates_sorted_list.md) | Simple sorted-list pointer skipping. |
| 5 | [Remove Duplicates from Sorted List II](problems/05_remove_duplicates_sorted_list_ii.md) | Dummy node plus duplicate-run removal. |
| 6 | [Partition List](problems/06_partition_list.md) | Build two lists and reconnect. |
| 7 | [Odd Even Linked List](problems/07_odd_even_linked_list.md) | Rearrange by pointer weaving. |

## 2. Fast and Slow Pointers

| Order | Problem | Why solve now? |
|---:|---|---|
| 8 | [Middle of the Linked List](problems/08_middle_linked_list.md) | First fast/slow pointer pattern. |
| 9 | [Linked List Cycle](problems/09_linked_list_cycle.md) | Floyd cycle detection. |
| 10 | [Intersection of Two Linked Lists](problems/10_intersection_two_linked_lists.md) | Equalize path lengths with pointer switching. |
| 11 | [Remove Nth Node From End of List](problems/11_remove_nth_node_from_end.md) | Maintain an `n`-node gap. |
| 12 | [Palindrome Linked List](problems/12_palindrome_linked_list.md) | Find middle, reverse second half, compare. |
| 13 | [Find the Duplicate Number](problems/13_find_duplicate_number.md) | Apply cycle detection to array indices. |

## 3. Reversal and Reordering

| Order | Problem | Why solve now? |
|---:|---|---|
| 14 | [Swap Nodes in Pairs](problems/14_swap_nodes_in_pairs.md) | Small fixed-size pointer reversal. |
| 15 | [Reverse Linked List II](problems/15_reverse_linked_list_ii.md) | Reverse a sublist in-place. |
| 16 | [Reverse Nodes in k-Group](problems/16_reverse_nodes_k_group.md) | General fixed-size group reversal. |
| 17 | [Rotate List](problems/17_rotate_list.md) | Connect into a cycle, then cut. |
| 18 | [Reorder List](problems/18_reorder_list.md) | Split, reverse, and merge alternately. |

## 4. Number, Merge, and Heap Patterns

| Order | Problem | Why solve now? |
|---:|---|---|
| 19 | [Add Two Numbers](problems/19_add_two_numbers.md) | Carry handling while walking lists. |
| 20 | [Merge K Sorted Lists](problems/20_merge_k_sorted_lists.md) | Heap-based multi-list merge. |

## 5. Special Pointers and Multilevel Lists

| Order | Problem | Why solve now? |
|---:|---|---|
| 21 | [Copy List with Random Pointer](problems/21_copy_list_random_pointer.md) | Clone nodes with extra pointers. |
| 22 | [Flatten a Multilevel Doubly Linked List](problems/22_flatten_multilevel_doubly_linked_list.md) | DFS/stack over child pointers. |

## 6. Cache and Data Structure Design

| Order | Problem | Why solve now? |
|---:|---|---|
| 23 | [LRU Cache](problems/23_lru_cache.md) | Hash map plus doubly linked list. |
| 24 | [All O`one Data Structure](problems/24_all_oone_data_structure.md) | Bucketed doubly linked list design. |
| 25 | [LFU Cache](problems/25_lfu_cache.md) | Frequency buckets plus recency. |

## Problems Added

The original list already covered the major linked-list interview set. I added these bridge problems:

- Delete Node in a Linked List
- Middle of the Linked List

They make local pointer mutation and fast/slow pointer movement easier before the harder variants.
