# Vertical Order Traversal of a Binary Tree

## Question

Given the `root` of a binary tree, return the **vertical order traversal** of its nodes' values.

For each node at position `(row, col)`, its left and right children will be at positions `(row + 1, col - 1)` and `(row + 1, col + 1)` respectively. The root of the tree is at `(0, 0)`.

The vertical order traversal of a binary tree is a list of top-to-bottom orderings for each column index starting from the leftmost column and ending on the rightmost column. There may be multiple nodes in the same row and column. In such cases, nodes should be sorted by their values.

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
Column  0: [3, 15]  (sorted: 3 < 15)
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

Column 0 has nodes 1, 5, 6 at same position - sorted by value: [1, 5, 6]
```

### Example 3
```
Input: root = [1,2,3,4,6,5,7]
          1
         / \
        2   3
       / \ / \
      4  6 5  7

Output: [[4], [2], [1, 5, 6], [3], [7]]

Note: At column 0, nodes 5 and 6 are at same (row, col) - sorted: [5, 6]
```

## Constraints

- The number of nodes in the tree is in the range `[1, 1000]`.
- `0 <= Node.val <= 1000`

## Solution Approaches

### Approach 1: BFS with Sorting
```python
from collections import deque, defaultdict

def verticalTraversal(root):
    if not root:
        return []
    
    # Map (col, row) to list of values
    column_map = defaultdict(list)
    
    # Queue stores (node, row, col)
    queue = deque([(root, 0, 0)])
    
    min_col = max_col = 0
    
    while queue:
        node, row, col = queue.popleft()
        
        column_map[col].append((row, node.val))
        min_col = min(min_col, col)
        max_col = max(max_col, col)
        
        if node.left:
            queue.append((node.left, row + 1, col - 1))
        if node.right:
            queue.append((node.right, row + 1, col + 1))
    
    # Build result
    result = []
    for col in range(min_col, max_col + 1):
        # Sort by row first, then by value
        values = [val for row, val in sorted(column_map[col])]
        result.append(values)
    
    return result
```

### Approach 2: DFS with Sorting
```python
def verticalTraversal(root):
    if not root:
        return []
    
    # Map col to list of (row, value)
    column_map = defaultdict(list)
    
    def dfs(node, row, col):
        if not node:
            return
        
        column_map[col].append((row, node.val))
        
        dfs(node.left, row + 1, col - 1)
        dfs(node.right, row + 1, col + 1)
    
    dfs(root, 0, 0)
    
    # Build result sorted by column, then row, then value
    result = []
    for col in sorted(column_map.keys()):
        # Sort by row first, then by value for same position
        values = [val for row, val in sorted(column_map[col])]
        result.append(values)
    
    return result
```

### Approach 3: Using Heap for Automatic Sorting
```python
import heapq
from collections import defaultdict

def verticalTraversal(root):
    if not root:
        return []
    
    # Min-heap: (col, row, value)
    heap = []
    
    def dfs(node, row, col):
        if not node:
            return
        
        heapq.heappush(heap, (col, row, node.val))
        
        dfs(node.left, row + 1, col - 1)
        dfs(node.right, row + 1, col + 1)
    
    dfs(root, 0, 0)
    
    # Group by column
    result = []
    current_col = None
    
    while heap:
        col, row, val = heapq.heappop(heap)
        
        if col != current_col:
            current_col = col
            result.append([])
        
        result[-1].append(val)
    
    return result
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| BFS with sorting | O(n log n) | O(n) |
| DFS with sorting | O(n log n) | O(n) |
| Heap approach | O(n log n) | O(n) |

Where n = number of nodes (sorting dominates)

## Key Insights

- **Sorting criteria**: Sort by column, then row, then value
- **Same position**: If two nodes have same (row, col), sort by value
- **BFS vs DFS**: BFS naturally processes top-to-bottom, but still need to sort same-position nodes

## Visual Explanation

```
Tree:
          1              Positions (row, col):
         / \             (0,0): 1
        2   3            (-1,1): 2, (1,1): 3  <- col, row
       / \ / \           (-2,2): 4, (0,2): 5,6, (2,2): 7
      4  5 6  7          

Grouped by column:
Column -2: [(2, 4)] -> [4]
Column -1: [(1, 2)] -> [2]
Column  0: [(0, 1), (2, 5), (2, 6)] -> sorted by row, then value -> [1, 5, 6]
Column  1: [(1, 3)] -> [3]
Column  2: [(2, 7)] -> [7]

Result: [[4], [2], [1, 5, 6], [3], [7]]
```

## Difference from Problem 39

| Aspect | Problem 39 | Problem 40 |
|--------|------------|------------|
| Same position | Order doesn't matter | Sort by value |
| Sorting | Only by row | By row, then value |
| Difficulty | Medium | Hard |

## Algorithm Steps

1. Traverse tree, recording (row, col, value) for each node
2. Group nodes by column
3. For each column, sort nodes by row, then by value
4. Build result list

## Related Problems

- [Binary Tree Vertical Order Traversal](problems/39_binary_tree_vertical_order_traversal.md) - Easier version
- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md)