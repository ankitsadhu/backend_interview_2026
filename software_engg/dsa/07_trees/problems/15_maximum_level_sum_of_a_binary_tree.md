# Maximum Level Sum of a Binary Tree

## Question

Given the `root` of a binary tree, return the **smallest level** `x` such that the sum of all the values of nodes at level `x` is **maximal**.

The root is at level 1, its children are at level 2, and so on.

## Examples

### Example 1
```
Input: root = [1,7,0,7,-8,null,null]
           1              <- Level 1: sum = 1
         /   \
        7     0           <- Level 2: sum = 7 + 0 = 7
       / \
      7  -8               <- Level 3: sum = 7 + (-8) = -1

Output: 2
Explanation: Level 2 has the maximum sum of 7
```

### Example 2
```
Input: root = [989,null,10250,98693,-89388,null,null,null,-32127]
           989                      <- Level 1: sum = 989
             \
             10250                  <- Level 2: sum = 10250
             /
          98693                     <- Level 3: sum = 98693
          /
       -89388                       <- Level 4: sum = -89388
        \
        -32127                      <- Level 5: sum = -32127

Output: 3
Explanation: Level 3 has the maximum sum of 98693
```

### Example 3
```
Input: root = [1,2,3,4,5,6,7]
           1              <- Level 1: sum = 1
         /   \
        2     3           <- Level 2: sum = 5
       / \   / \
      4   5 6   7         <- Level 3: sum = 22

Output: 3
```

## Constraints

- The number of nodes in the tree is in the range `[1, 10^4]`.
- `-10^5 <= Node.val <= 10^5`

## Solution Approaches

### Approach 1: BFS (Level Order Traversal)
```python
from collections import deque

def maxLevelSum(root):
    if not root:
        return 0
    
    max_sum = float('-inf')
    max_level = 1
    current_level = 1
    
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        level_sum = 0
        
        for _ in range(level_size):
            node = queue.popleft()
            level_sum += node.val
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        # Update max if current level sum is greater
        if level_sum > max_sum:
            max_sum = level_sum
            max_level = current_level
        
        current_level += 1
    
    return max_level
```

### Approach 2: Recursive DFS
```python
def maxLevelSum(root):
    level_sums = []
    
    def dfs(node, level):
        if not node:
            return
        
        # Extend list if needed
        if level == len(level_sums):
            level_sums.append(0)
        
        # Add to level sum
        level_sums[level] += node.val
        
        dfs(node.left, level + 1)
        dfs(node.right, level + 1)
    
    dfs(root, 0)
    
    # Find level with maximum sum (1-indexed)
    max_sum = max(level_sums)
    return level_sums.index(max_sum) + 1
```

### Approach 3: DFS with Tracking Max
```python
def maxLevelSum(root):
    level_sums = {}
    
    def dfs(node, level):
        if not node:
            return
        
        level_sums[level] = level_sums.get(level, 0) + node.val
        dfs(node.left, level + 1)
        dfs(node.right, level + 1)
    
    dfs(root, 1)  # Root is at level 1
    
    # Find level with maximum sum
    max_level = 1
    max_sum = float('-inf')
    
    for level, total in level_sums.items():
        if total > max_sum:
            max_sum = total
            max_level = level
    
    return max_level
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| BFS | O(n) | O(w) - queue width |
| Recursive DFS | O(n) | O(h) - recursion + list |
| DFS with dict | O(n) | O(h) - recursion + dict |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Level order traversal**: Process nodes level by level to calculate sums
- **Track maximum**: Keep track of both the maximum sum and its level
- **Smallest level**: If multiple levels have the same max sum, return the smallest level
- **1-indexed**: Levels are 1-indexed (root is level 1)

## Algorithm Steps

1. Initialize `max_sum = -infinity` and `max_level = 1`
2. Perform level order traversal using BFS
3. For each level:
   - Calculate the sum of all node values
   - If sum > max_sum, update max_sum and max_level
4. Return max_level

## Related Problems

- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md) - Get all nodes at each level
- [Binary Tree Right Side View](problems/13_binary_tree_right_side_view.md) - Get rightmost node at each level
- [Maximum Width of Binary Tree](problems/14_maximum_width_of_binary_tree.md) - Find widest level