# Binary Tree Right Side View

## Question

Given the `root` of a binary tree, imagine yourself standing on the **right side** of it, return the values of the nodes you can see ordered from top to bottom.

In other words, return the **rightmost node** at each level of the tree.

## Examples

### Example 1
```
Input: root = [1,2,3,null,5,null,4]
       1            <- View from right: 1
      / \
     2   3          <- View from right: 3
      \   \
       5   4        <- View from right: 4

Output: [1, 3, 4]
```

### Example 2
```
Input: root = [1,null,3]
       1
        \
         3

Output: [1, 3]
```

### Example 3
```
Input: root = []
Output: []
```

### Example 4
```
Input: root = [1,2,3,4]
       1
      / \
     2   3
    /
   4

Output: [1, 3, 4]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 100]`.
- `-100 <= Node.val <= 100`

## Solution Approaches

### Approach 1: Iterative BFS (Level Order)
```python
from collections import deque

def rightSideView(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        
        for i in range(level_size):
            node = queue.popleft()
            
            # Add the last node of each level to result
            if i == level_size - 1:
                result.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    
    return result
```

### Approach 2: Recursive DFS (Priority to Right)
```python
def rightSideView(root):
    result = []
    
    def dfs(node, level):
        if not node:
            return
        
        # If this is the first node we're seeing at this level, add it
        if level == len(result):
            result.append(node.val)
        
        # Visit right child first to get rightmost node
        dfs(node.right, level + 1)
        dfs(node.left, level + 1)
    
    dfs(root, 0)
    return result
```

### Approach 3: Iterative DFS
```python
def rightSideView(root):
    if not root:
        return []
    
    result = []
    stack = [(root, 0)]
    
    while stack:
        node, level = stack.pop()
        
        # If this is the first node at this level, add it
        if level == len(result):
            result.append(node.val)
        
        # Push left first so right is processed first
        if node.left:
            stack.append((node.left, level + 1))
        if node.right:
            stack.append((node.right, level + 1))
    
    return result
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Iterative BFS | O(n) | O(w) - queue width |
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative DFS | O(n) | O(h) - explicit stack |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **BFS approach**: The last node processed at each level is the rightmost
- **DFS approach**: Visit right child before left child; first node at each level is rightmost
- **Level tracking**: Use `level == len(result)` to detect first visit to a new level

## Visual Explanation

```
Tree:              Right Side View:
       1                 1
      / \               
     2   3      =>      3
      \   \             
       5   4            4

At each level, we see the rightmost node
```

## Left Side View Variation

To get the **left side view**, simply:
- In BFS: Take the **first** node of each level (`i == 0`)
- In DFS: Visit **left** child before right child

```python
def leftSideView(root):
    result = []
    
    def dfs(node, level):
        if not node:
            return
        if level == len(result):
            result.append(node.val)
        dfs(node.left, level + 1)   # Left first
        dfs(node.right, level + 1)
    
    dfs(root, 0)
    return result
```

## Related Problems

- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md) - Get all nodes at each level
- [Maximum Width of Binary Tree](problems/14_maximum_width_of_binary_tree.md) - Find widest level
- [Find Bottom Left Tree Value](problems/) - Get leftmost node at bottom level