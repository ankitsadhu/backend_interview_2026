# Maximum Depth of Binary Tree

## Question

Given the `root` of a binary tree, return its maximum depth.

A binary tree's **maximum depth** is the number of nodes along the longest path from the root node down to the farthest leaf node.

**Note**: A leaf is a node with no children.

## Examples

### Example 1
```
Input: root = [3,9,20,null,null,15,7]
       3
      / \
     9  20
       /  \
      15   7

Output: 3
```

### Example 2
```
Input: root = [1,null,2]
       1
        \
         2

Output: 2
```

### Example 3
```
Input: root = []
Output: 0
```

### Example 4
```
Input: root = [0]
Output: 1
```

## Constraints

- The number of nodes in the tree is in the range `[0, 10^4]`.
- `-100 <= Node.val <= 100`

## Solution Approaches

### Approach 1: Recursive DFS (Top-Down)
```python
def maxDepth(root):
    if not root:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```

### Approach 2: Iterative BFS (Level Order)
```python
from collections import deque

def maxDepth(root):
    if not root:
        return 0
    
    queue = deque([root])
    depth = 0
    
    while queue:
        level_size = len(queue)
        for _ in range(level_size):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        depth += 1
    
    return depth
```

### Approach 3: Iterative DFS with Stack
```python
def maxDepth(root):
    if not root:
        return 0
    
    stack = [(root, 1)]
    max_depth = 0
    
    while stack:
        node, depth = stack.pop()
        max_depth = max(max_depth, depth)
        if node.left:
            stack.append((node.left, depth + 1))
        if node.right:
            stack.append((node.right, depth + 1))
    
    return max_depth
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative BFS | O(n) | O(w) - queue width |
| Iterative DFS | O(n) | O(h) - explicit stack |

Where n = number of nodes, h = height of tree, w = maximum width of tree

## Key Insights

- **Base case**: Empty tree has depth 0
- **Recursive relation**: `depth(node) = 1 + max(depth(left), depth(right))`
- **BFS advantage**: Naturally processes level by level, easy to count depth