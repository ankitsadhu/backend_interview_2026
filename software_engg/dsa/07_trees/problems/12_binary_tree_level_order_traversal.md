'S# Binary Tree Level Order Traversal

## Question

Given the `root` of a binary tree, return the **level order traversal** of its nodes' values.

Level order traversal means visiting nodes from left to right, level by level (also known as Breadth-First Search or BFS).

## Examples

### Example 1
```
Input: root = [3,9,20,null,null,15,7]
       3
      / \
     9  20
       /  \
      15   7

Output: [[3], [9, 20], [15, 7]]
```

### Example 2
```
Input: root = [1]
       1

Output: [[1]]
```

### Example 3
```
Input: root = []
Output: []
```

### Example 4
```
Input: root = [1,2,3,4,null,null,5]
          1
         / \
        2   3
       /     \
      4       5

Output: [[1], [2, 3], [4, 5]]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 2000]`.
- `-1000 <= Node.val <= 1000`

## Solution Approaches

### Approach 1: Iterative BFS (Standard)
```python
from collections import deque

def levelOrder(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        current_level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(current_level)
    
    return result
```

### Approach 2: Recursive DFS
```python
def levelOrder(root):
    result = []
    
    def dfs(node, level):
        if not node:
            return
        
        # Start a new level if needed
        if level == len(result):
            result.append([])
        
        # Add node to its level
        result[level].append(node.val)
        
        # Recurse for children
        dfs(node.left, level + 1)
        dfs(node.right, level + 1)
    
    dfs(root, 0)
    return result
```

### Approach 3: BFS without inner loop
```python
from collections import deque

def levelOrder(root):
    if not root:
        return []
    
    result = []
    queue = deque([(root, 0)])  # (node, level)
    
    while queue:
        node, level = queue.popleft()
        
        # Start a new level if needed
        if level == len(result):
            result.append([])
        
        result[level].append(node.val)
        
        if node.left:
            queue.append((node.left, level + 1))
        if node.right:
            queue.append((node.right, level + 1))
    
    return result
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Iterative BFS | O(n) | O(w) - queue width |
| Recursive DFS | O(n) | O(h) - recursion stack |
| BFS with level | O(n) | O(w) - queue |

Where n = number of nodes, h = height of tree, w = maximum width of tree

## Key Insights

- **Level tracking**: Use `level_size = len(queue)` to process one level at a time
- **Left to right**: Add left child before right child to maintain order
- **Empty tree**: Handle edge case of empty root

## Level Order Traversal Pattern

```python
# Standard template for level order traversal
queue = deque([root])
while queue:
    level_size = len(queue)  # Number of nodes at current level
    current_level = []
    
    for _ in range(level_size):
        node = queue.popleft()
        current_level.append(node.val)
        
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    
    result.append(current_level)
```

## Related Problems

- [Binary Tree Right Side View](problems/13_binary_tree_right_side_view.md) - Get rightmost node at each level
- [Maximum Width of Binary Tree](problems/14_maximum_width_of_binary_tree.md) - Find widest level
- [Maximum Level Sum of a Binary Tree](problems/15_maximum_level_sum_of_a_binary_tree.md) - Find level with max sum