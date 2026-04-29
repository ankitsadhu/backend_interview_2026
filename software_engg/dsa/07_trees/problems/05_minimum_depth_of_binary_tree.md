# Minimum Depth of Binary Tree

## Question

Given the `root` of a binary tree, find its **minimum depth**.

The minimum depth is the number of nodes along the shortest path from the root node down to the nearest leaf node.

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

Output: 2
Explanation: The shortest path is 3 -> 9 (or 3 -> 20 -> 15 or 3 -> 20 -> 7)
```

### Example 2
```
Input: root = [2,null,3,null,4,null,5,null,6]
       2
        \
         3
          \
           4
            \
             5
              \
               6

Output: 5
```

### Example 3
```
Input: root = [1,2,3,4,5]
       1
      / \
     2   3
    / \
   4   5

Output: 2
```

### Example 4
```
Input: root = []
Output: 0
```

## Constraints

- The number of nodes in the tree is in the range `[0, 10^5]`.
- `-1000 <= Node.val <= 1000`

## Common Mistake

⚠️ **Important**: A leaf node is a node with **no children**. A node with only one child is NOT a leaf.

```
Input: [1,2]
       1
      /
     2

Wrong answer: 1 (counting root only)
Correct answer: 2 (root -> leaf node 2)
```

## Solution Approaches

### Approach 1: Recursive DFS
```python
def minDepth(root):
    if not root:
        return 0
    
    # If no children, this is a leaf
    if not root.left and not root.right:
        return 1
    
    # If only one child exists, must go through that child
    if not root.left:
        return 1 + minDepth(root.right)
    if not root.right:
        return 1 + minDepth(root.left)
    
    # Both children exist
    return 1 + min(minDepth(root.left), minDepth(root.right))
```

### Approach 2: Iterative BFS (Optimal for minimum depth)
```python
from collections import deque

def minDepth(root):
    if not root:
        return 0
    
    queue = deque([(root, 1)])
    
    while queue:
        node, depth = queue.popleft()
        
        # First leaf found is the minimum depth
        if not node.left and not node.right:
            return depth
        
        if node.left:
            queue.append((node.left, depth + 1))
        if node.right:
            queue.append((node.right, depth + 1))
    
    return 0
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative BFS | O(n) | O(w) - queue width |

Where n = number of nodes, h = height of tree, w = maximum width of tree

## Key Insights

- **BFS is optimal** for finding minimum depth because it explores level by level
- **Handle edge cases**: Node with only one child is not a leaf
- **Early termination**: BFS can return as soon as first leaf is found

## Comparison with Maximum Depth

| Aspect | Maximum Depth | Minimum Depth |
|--------|---------------|---------------|
| Definition | Longest path to any leaf | Shortest path to nearest leaf |
| Edge case | None | Single child nodes |
| Optimal approach | DFS or BFS | BFS (early termination) |