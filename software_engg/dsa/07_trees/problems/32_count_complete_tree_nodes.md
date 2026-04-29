# Count Complete Tree Nodes

## Question

Given the `root` of a **complete binary tree**, count the number of nodes.

A **complete binary tree** is a binary tree in which every level, except possibly the last, is completely filled, and all nodes are as far left as possible.

Design an algorithm that runs in less than `O(n)` time complexity.

## Examples

### Example 1
```
Input: root = [1,2,3,4,5,6]
        1
       / \
      2   3
     / \ /
    4  5 6

Output: 6
```

### Example 2
```
Input: root = []
Output: 0
```

### Example 3
```
Input: root = [1]
Output: 1
```

## Constraints

- The number of nodes in the tree is in the range `[0, 5 * 10^4]`.
- `0 <= Node.val <= 5 * 10^4`
- The tree is guaranteed to be complete.

## Solution Approaches

### Approach 1: Simple DFS/BFS (O(n) - Not optimal)
```python
def countNodes(root):
    if not root:
        return 0
    return 1 + countNodes(root.left) + countNodes(root.right)
```

### Approach 2: Using Complete Tree Property (O(log^2 n))
```python
def countNodes(root):
    if not root:
        return 0
    
    # Calculate left and right heights
    left_height = get_left_height(root)
    right_height = get_right_height(root)
    
    # If left and right heights are equal, it's a perfect binary tree
    if left_height == right_height:
        return (1 << left_height) - 1  # 2^height - 1
    
    # Otherwise, recursively count left and right subtrees
    return 1 + countNodes(root.left) + countNodes(root.right)

def get_left_height(node):
    height = 0
    while node:
        height += 1
        node = node.left
    return height

def get_right_height(node):
    height = 0
    while node:
        height += 1
        node = node.right
    return height
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Simple DFS | O(n) | O(h) - recursion |
| Complete tree property | O(log^2 n) | O(h) - recursion |

Where n = number of nodes, h = height of tree

## Key Insights

- **Perfect binary tree**: If left height == right height, tree is perfect
- **Formula for perfect tree**: Number of nodes = 2^h - 1
- **Complete tree**: At most one subtree is not perfect

## Visual Explanation

```
Complete Tree:
        1              left_height = 3
       / \             right_height = 2
      2   3            Not equal, so not perfect
     / \ /
    4  5 6

    Count = 1 + count(2's subtree) + count(3's subtree)

Perfect Subtree:
        2              left_height = 2
       / \             right_height = 2
      4   5            Equal! Perfect subtree
                       Count = 2^2 - 1 = 3
```

## Algorithm Steps

1. Calculate the height of the leftmost path
2. Calculate the height of the rightmost path
3. If heights are equal, the tree is perfect: return 2^h - 1
4. Otherwise, recursively count nodes in left and right subtrees

## Why O(log^2 n)?

- At each level, we compute heights in O(log n)
- We recurse down one path of length O(log n)
- Total: O(log n) * O(log n) = O(log^2 n)

## Related Problems

- [Maximum Depth of Binary Tree](problems/04_maximum_depth_of_binary_tree.md)
- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md)