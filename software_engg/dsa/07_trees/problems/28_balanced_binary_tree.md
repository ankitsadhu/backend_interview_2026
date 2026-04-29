# Balanced Binary Tree

## Question

Given a binary tree, determine if it is **height-balanced**.

A **height-balanced** binary tree is defined as a binary tree in which the left and right subtrees of **every node** differ in height by no more than 1.

## Examples

### Example 1
```
Input: root = [3,9,20,null,null,15,7]
       3
      / \
     9  20
       /  \
      15   7

Output: true
Explanation: All nodes have subtrees that differ in height by at most 1.
```

### Example 2
```
Input: root = [1,2,2,3,3,null,null,4,4]
          1
         / \
        2   2
       / \
      3   3
     / \
    4   4

Output: false
Explanation: Node 2 (left child of root) has left subtree height 2 and right subtree height 0.
```

### Example 3
```
Input: root = []
Output: true
Explanation: Empty tree is balanced.
```

## Constraints

- The number of nodes in the tree is in the range `[0, 5000]`.
- `-10^4 <= Node.val <= 10^4`

## Solution Approaches

### Approach 1: Top-Down Recursive (Inefficient)
```python
def isBalanced(root):
    if not root:
        return True
    
    def height(node):
        if not node:
            return 0
        return 1 + max(height(node.left), height(node.right))
    
    # Check current node and recursively check children
    return (abs(height(root.left) - height(root.right)) <= 1 and
            isBalanced(root.left) and
            isBalanced(root.right))
```

### Approach 2: Bottom-Up Recursive (Optimal)
```python
def isBalanced(root):
    def check_height(node):
        if not node:
            return 0
        
        # Check left subtree
        left_height = check_height(node.left)
        if left_height == -1:
            return -1
        
        # Check right subtree
        right_height = check_height(node.right)
        if right_height == -1:
            return -1
        
        # Check if current node is balanced
        if abs(left_height - right_height) > 1:
            return -1
        
        return 1 + max(left_height, right_height)
    
    return check_height(root) != -1
```

### Approach 3: Iterative with Stack
```python
def isBalanced(root):
    if not root:
        return True
    
    # Map to store heights
    height = {}
    stack = []
    current = root
    last_visited = None
    
    while stack or current:
        if current:
            stack.append(current)
            current = current.left
        else:
            peek = stack[-1]
            if peek.right and last_visited != peek.right:
                current = peek.right
            else:
                # Process node
                left_h = height.get(peek.left, 0)
                right_h = height.get(peek.right, 0)
                
                if abs(left_h - right_h) > 1:
                    return False
                
                height[peek] = 1 + max(left_h, right_h)
                last_visited = stack.pop()
    
    return True
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Top-down | O(n log n) | O(h) - recursion |
| Bottom-up | O(n) | O(h) - recursion |
| Iterative | O(n) | O(h) - stack + map |

Where n = number of nodes, h = height of tree

## Key Insights

- **Bottom-up is optimal**: Compute height while checking balance
- **Early termination**: Return -1 to indicate unbalanced subtree
- **Single pass**: Each node visited exactly once in bottom-up approach

## Visual Explanation

```
Balanced Tree:           Unbalanced Tree:
       3                        1
      / \                      / \
     9  20                    2   2
       /  \                  / \
      15   7                3   3
                           / \
                          4   4

Heights:                 Heights:
- Node 9: 0              - Node 4: 0
- Node 15: 0             - Node 3: 1
- Node 7: 0              - Node 2 (left): 2
- Node 20: 1             - Node 2 (right): 0
- Node 3: 2              - Node 1: 3

All differences ≤ 1      Node 2 has diff = 2 > 1
=> Balanced              => Not Balanced
```

## Algorithm Steps (Bottom-Up)

1. Recursively compute height of left subtree
2. If left subtree is unbalanced, return -1
3. Recursively compute height of right subtree
4. If right subtree is unbalanced, return -1
5. If current node is unbalanced (diff > 1), return -1
6. Otherwise, return height of current subtree

## Why Bottom-Up is Better?

- **Top-down**: Recalculates height for same nodes multiple times
- **Bottom-up**: Each node's height computed only once

## Related Problems

- [Maximum Depth of Binary Tree](problems/04_maximum_depth_of_binary_tree.md)
- [Diameter of Binary Tree](problems/27_diameter_of_binary_tree.md)
- [Same Tree](problems/06_same_tree.md)