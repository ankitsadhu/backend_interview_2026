# Maximum Width of Binary Tree

## Question

Given the `root` of a binary tree, return the **maximum width** of the given tree.

The **maximum width** of a tree is the maximum **width** among all levels.

The **width** of one level is defined as the length between the leftmost and rightmost non-null nodes, including any null nodes that would exist in a complete binary tree at that level.

## Examples

### Example 1
```
Input: root = [1,3,2,5,3,null,9]
           1                  <- Level 1: width = 1
         /   \
        3     2               <- Level 2: width = 2
       / \     \
      5   3     9            <- Level 3: width = 4 (positions 0,1,2,3)

Output: 4
Explanation: Maximum width exists at level 3 (5,3,null,9)
```

### Example 2
```
Input: root = [1,3,2,5,null,null,9,6,null,7]
           1                    <- Level 1: width = 1
         /   \
        3     2                 <- Level 2: width = 2
       /       \
      5         9              <- Level 3: width = 2
     /           \
    6             7            <- Level 4: width = 4 (with nulls in between)

Output: 7
Explanation: At level 4, positions span from 6 to 7 with nulls in between
```

### Example 3
```
Input: root = [1,3,2,5]
       1
      / \
     3   2
    /
   5

Output: 2
Explanation: Maximum width at level 2
```

## Constraints

- The number of nodes in the tree is in the range `[1, 3000]`.
- `-100 <= Node.val <= 100`

## Solution Approaches

### Approach 1: BFS with Position Indexing
```python
from collections import deque

def widthOfBinaryTree(root):
    if not root:
        return 0
    
    max_width = 0
    queue = deque([(root, 0)])  # (node, position)
    
    while queue:
        level_size = len(queue)
        _, level_start = queue[0]  # Position of first node in level
        _, level_end = queue[-1]   # Position of last node in level
        
        # Width = end - start + 1
        max_width = max(max_width, level_end - level_start + 1)
        
        for _ in range(level_size):
            node, pos = queue.popleft()
            
            if node.left:
                queue.append((node.left, 2 * pos))
            if node.right:
                queue.append((node.right, 2 * pos + 1))
    
    return max_width
```

### Approach 2: DFS with Position Tracking
```python
def widthOfBinaryTree(root):
    # Store the first position seen at each level
    leftmost = {}
    max_width = 0
    
    def dfs(node, level, pos):
        nonlocal max_width
        
        if not node:
            return
        
        # Record first position at this level
        if level not in leftmost:
            leftmost[level] = pos
        
        # Calculate width at this level
        max_width = max(max_width, pos - leftmost[level] + 1)
        
        # Recurse with position indexing
        dfs(node.left, level + 1, 2 * pos)
        dfs(node.right, level + 1, 2 * pos + 1)
    
    dfs(root, 0, 0)
    return max_width
```

### Approach 3: BFS with Offset Normalization
```python
from collections import deque

def widthOfBinaryTree(root):
    if not root:
        return 0
    
    max_width = 0
    queue = deque([(root, 0)])
    
    while queue:
        level_size = len(queue)
        _, level_offset = queue[0]  # Normalize positions
        
        first_pos = None
        last_pos = None
        
        for i in range(level_size):
            node, pos = queue.popleft()
            normalized_pos = pos - level_offset
            
            if i == 0:
                first_pos = normalized_pos
            if i == level_size - 1:
                last_pos = normalized_pos
            
            if node.left:
                queue.append((node.left, 2 * normalized_pos))
            if node.right:
                queue.append((node.right, 2 * normalized_pos + 1))
        
        max_width = max(max_width, last_pos - first_pos + 1)
    
    return max_width
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| BFS with indexing | O(n) | O(w) - queue width |
| DFS with tracking | O(n) | O(h) - recursion + dict |
| BFS with normalization | O(n) | O(w) - queue |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Position indexing**: In a complete binary tree, if parent is at position `i`:
  - Left child is at position `2 * i`
  - Right child is at position `2 * i + 1`
- **Width calculation**: `width = rightmost_position - leftmost_position + 1`
- **Include nulls**: Width includes positions where null nodes would exist

## Position Indexing Visualization

```
Complete Binary Tree with positions:
           0
         /   \
        0     1
       / \   / \
      0   1 2   3
     /\  /\ /\  /\
    0 1 2 3 4 5 6 7

For node at position i:
- Left child: 2*i
- Right child: 2*i + 1
```

## Important Note

⚠️ **Overflow Prevention**: For very deep trees, positions can become very large. In languages with fixed-size integers, you may need to normalize positions at each level by subtracting the minimum position.

## Related Problems

- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md) - Get all nodes at each level
- [Binary Tree Right Side View](problems/13_binary_tree_right_side_view.md) - Get rightmost node at each level