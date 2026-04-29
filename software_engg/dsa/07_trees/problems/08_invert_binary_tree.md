# Invert Binary Tree

## Question

Given the `root` of a binary tree, invert the tree, and return its root.

**Inverting a binary tree** means swapping all left and right child nodes at every level, effectively creating a mirror image of the original tree.

## Examples

### Example 1
```
Input: root = [4,2,7,1,3,6,9]
       4            4
      / \          / \
     2   7   =>   7   2
    / \ / \      / \ / \
   1  3 6  9    9  6 3  1

Output: [4,7,2,9,6,3,1]
```

### Example 2
```
Input: root = [2,1,3]
       2          2
      / \   =>   / \
     1   3      3   1

Output: [2,3,1]
```

### Example 3
```
Input: root = []
Output: []
```

### Example 4
```
Input: root = [1,2]
       1        1
      /   =>     \
     2            2

Output: [1,null,2]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 100]`.
- `-100 <= Node.val <= 100`

## Solution Approaches

### Approach 1: Recursive DFS (Preorder)
```python
def invertTree(root):
    if not root:
        return None
    
    # Swap left and right children
    root.left, root.right = root.right, root.left
    
    # Recursively invert subtrees
    invertTree(root.left)
    invertTree(root.right)
    
    return root
```

### Approach 2: Recursive DFS (Postorder)
```python
def invertTree(root):
    if not root:
        return None
    
    # First invert subtrees
    left = invertTree(root.left)
    right = invertTree(root.right)
    
    # Then swap
    root.left = right
    root.right = left
    
    return root
```

### Approach 3: Iterative BFS (Level Order)
```python
from collections import deque

def invertTree(root):
    if not root:
        return None
    
    queue = deque([root])
    
    while queue:
        node = queue.popleft()
        
        # Swap children
        node.left, node.right = node.right, node.left
        
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    
    return root
```

### Approach 4: Iterative DFS (Stack)
```python
def invertTree(root):
    if not root:
        return None
    
    stack = [root]
    
    while stack:
        node = stack.pop()
        
        # Swap children
        node.left, node.right = node.right, node.left
        
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    
    return root
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative BFS | O(n) | O(w) - queue width |
| Iterative DFS | O(n) | O(h) - explicit stack |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Simple swap**: At each node, just swap left and right children
- **All traversals work**: Preorder, postorder, level-order all work equally well
- **In-place operation**: Can be done without creating new nodes

## Famous Context

This problem became famous after Max Howell (creator of Homebrew) tweeted:
> "Google: 90% of our engineers use the software you wrote (Homebrew), but you can't invert a binary tree on a whiteboard so fuck off."

The point was that even simple tree problems are important for software engineering interviews.

## Related Problems

- [Symmetric Tree](problems/07_symmetric_tree.md) - Check if tree is mirror of itself
- [Maximum Depth of Binary Tree](problems/04_maximum_depth_of_binary_tree.md) - Find tree height