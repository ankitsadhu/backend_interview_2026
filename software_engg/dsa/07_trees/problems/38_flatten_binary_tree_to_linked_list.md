# Flatten Binary Tree to Linked List

## Question

Given the `root` of a binary tree, flatten the tree into a "linked list" in-place.

The "linked list" should use the same `TreeNode` class where the `right` child pointer points to the next node in the list and the `left` child pointer is always `null`.

The "linked list" should be in the same order as a **preorder traversal** of the binary tree.

## Examples

### Example 1
```
Input: root = [1,2,5,3,4,null,6]
       1
      / \
     2   5
    / \   \
   3   4   6

Output: [1,null,2,null,3,null,4,null,5,null,6]
1 -> 2 -> 3 -> 4 -> 5 -> 6

Visual:
1
 \
  2
   \
    3
     \
      4
       \
        5
         \
          6
```

### Example 2
```
Input: root = []
Output: []
```

### Example 3
```
Input: root = [0]
Output: [0]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 2000]`.
- `-100 <= Node.val <= 100`

## Follow-up

Can you flatten the tree in-place (with O(1) extra space)?

## Solution Approaches

### Approach 1: Recursive (Reverse Preorder)
```python
def flatten(root):
    if not root:
        return None
    
    # Flatten right subtree first, then left
    flatten(root.right)
    flatten(root.left)
    
    # Connect current node to previously processed node
    root.right = prev
    root.left = None
    
    # Update prev to current node
    prev = root

# Note: prev needs to be a class variable or passed by reference
```

### Approach 2: Iterative with Stack
```python
def flatten(root):
    if not root:
        return
    
    stack = [root]
    prev = None
    
    while stack:
        node = stack.pop()
        
        # Connect previous node to current
        if prev:
            prev.right = node
            prev.left = None
        
        # Push right first, then left (so left is processed first)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
        
        prev = node
```

### Approach 3: Morris Traversal (O(1) Space)
```python
def flatten(root):
    current = root
    
    while current:
        if current.left:
            # Find the rightmost node in left subtree
            predecessor = current.left
            while predecessor.right:
                predecessor = predecessor.right
            
            # Connect right subtree to the rightmost of left
            predecessor.right = current.right
            
            # Move left subtree to right
            current.right = current.left
            current.left = None
        
        current = current.right
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(n) | O(h) - recursion stack |
| Iterative with stack | O(n) | O(h) - explicit stack |
| Morris traversal | O(n) | O(1) - in-place |

Where n = number of nodes, h = height of tree

## Key Insights

- **Preorder traversal**: The flattened list follows preorder sequence
- **In-place modification**: Can be done without extra space using Morris traversal
- **Rightmost predecessor**: Find rightmost node of left subtree to connect

## Visual Explanation

```
Original tree:
       1
      / \
     2   5
    / \   \
   3   4   6

Morris traversal steps:
1. At node 1: left exists
   - Find predecessor: 4 (rightmost of left subtree)
   - Connect 4.right = 5 (current.right)
   - Move left to right: 1.right = 2, 1.left = null

       1
        \
         2
        / \
       3   4
            \
             5
              \
               6

2. At node 2: left exists
   - Find predecessor: 3 (rightmost of left subtree)
   - Connect 3.right = 4
   - Move left to right: 2.right = 3, 2.left = null

       1
        \
         2
          \
           3
            \
             4
              \
               5
                \
                 6

Final flattened tree (linked list):
1 -> 2 -> 3 -> 4 -> 5 -> 6
```

## Algorithm Steps (Morris Traversal)

1. Start with current = root
2. While current is not null:
   - If current has a left child:
     a. Find the rightmost node in the left subtree (predecessor)
     b. Connect predecessor.right to current.right
     c. Move current.left to current.right
     d. Set current.left to null
   - Move to current.right
3. Tree is now flattened

## Related Problems

- [Binary Tree Inorder Traversal](problems/01_binary_tree_inorder_traversal.md)
- [Binary Search Tree Iterator](problems/25_binary_search_tree_iterator.md)
- [Populating Next Right Pointers in Each Node](problems/16_populating_next_right_pointers_in_each_node.md)