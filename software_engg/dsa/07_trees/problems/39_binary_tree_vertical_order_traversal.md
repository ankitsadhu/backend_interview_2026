# Binary Tree Vertical Order Traversal

## Question

Given the `root` of a binary tree, return the **vertical order traversal** of its nodes' values.

Vertical order means nodes are grouped by their column index, from leftmost column to rightmost column. Within each column, nodes should be ordered from top to bottom (by row).

## Examples

### Example 1
```
Input: root = [3,9,20,null,null,15,7]
       3
      / \
     9  20
       /  \
      15   7

Output: [[9], [3, 15], [20], [7]]

Column assignments:
Column -1: [9]
Column  0: [3, 15]  (3 is above 15)
Column  1: [20]
Column  2: [7]
```

### Example 2
```
Input: root = [1,2,3,4,5,6,7]
          1
         / \
        2   3
       / \ / \
      4  5 6  7

Output: [[4], [2], [1, 5, 6], [3], [7]]

Column assignments:
Column -2: [4]
Column -1: [2]
Column  0: [1, 5, 6]  (1 is above 5 and 6)
Column  1: [3]
Column  2: [7]
```

### Example 3
```
Input: root = [1,2,3,4,6,5,7]
          1
         / \
        2   3
       / \ / \
      4  6 5  7

Output: [[4], [2], [1, 6, 5], [3], [7]]

Note: 6 comes before 5 in column 0 because 6 is a left child (processed first)
```

## Constraints

- The number of nodes in the tree is in the range `[1, 1000]`.
- `-1000 <= Node.val <= 1000`

## Solution Approaches

### Approach: BFS with Column Index
```python
from collections import deque, defaultdict

def verticalOrder(root):
    if not root:
        return []
    
    # Map column index to list of node values
    column_map = defaultdict(list)
    
    # Queue stores (node, column_index)
    queue = deque([(root, 0)])
    
    min_col = max_col = 0
    
    while queue:
        node, col = queue.popleft()
        
        column_map[col].append(node.val)
        min_col = min(min_col, col)
        max_col = max(max_col, col)
        
        if node.left:
            queue.append((node.left, col - 1))
        if node.right:
            queue.append((node.right, col + 1))
    
    # Build result from min_col to max_col
    result = []
    for col in range(min_col, max_col + 1):
        result.append(column_map[col])
    
    return result
```

### Approach 2: DFS with Sorting
```python
def verticalOrder(root):
    if not root:
        return []
    
    # Map (col, row) to list of values
    column_map = defaultdict(list)
    
    def dfs(node, row, col):
        if not node:
            return
        
        column_map[col].append((row, node.val))
        
        dfs(node.left, row + 1, col - 1)
        dfs(node.right, row + 1, col + 1)
    
    dfs(root, 0, 0)
    
    # Sort by column, then by row
    result = []
    for col in sorted(column_map.keys()):
        # Sort values within column by row
        values = [val for row, val in sorted(column_map[col])]
        result.append(values)
    
    return result
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| BFS | O(n) | O(n) - queue + map |
| DFS with sorting | O(n log n) | O(n) - recursion + map |

Where n = number of nodes

## Key Insights

- **Column indexing**: Root is at column 0, left child at col-1, right at col+1
- **BFS ensures top-to-bottom**: Level order naturally processes nodes from top to bottom
- **Same position**: If two nodes have same (row, col), order doesn't matter per problem

## Visual Explanation

```
Tree:
          1              Column indices:
         / \             -2  -1   0   1   2
        2   3            __  __  __  __  __
       / \ / \                    
      4  5 6  7          -2: [4]
                         -1: [2]
Columns:                  0: [1, 5, 6]  (1 at row 0, 5,6 at row 2)
-2: 4                    1: [3]
-1: 2                    2: [7]
 0: 1, 5, 6
 1: 3
 2: 7

Result: [[4], [2], [1, 5, 6], [3], [7]]
```

## Algorithm Steps (BFS)

1. Initialize queue with (root, 0) where 0 is column index
2. While queue is not empty:
   - Pop node and its column
   - Add node value to column_map[column]
   - Add left child with column-1
   - Add right child with column+1
3. Sort columns and build result

## Related Problems

- [Vertical Order Traversal of a Binary Tree](problems/40_vertical_order_traversal_of_a_binary_tree.md) - Harder version with sorting
- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md)
- [Binary Tree Right Side View](problems/13_binary_tree_right_side_view.md)