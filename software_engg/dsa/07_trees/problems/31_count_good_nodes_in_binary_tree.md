# Count Good Nodes in Binary Tree

## Question

Given a binary tree `root`, return the number of **good nodes** in the binary tree.

A node `X` is named **good** if in the path from root to `X` there are no nodes with a value greater than `X.val`.

## Examples

### Example 1
```
Input: root = [3,1,4,3,null,1,5]
          3
         / \
        1   4
       /   / \
      3   1   5

Output: 4
Explanation: Good nodes are: 3 (root), 4, 5, and 3 (left subtree).
- Node 3: Path [3] - max is 3, node.val is 3 ✓
- Node 1: Path [3,1] - max is 3, node.val is 1 ✗
- Node 4: Path [3,4] - max is 4, node.val is 4 ✓
- Node 3: Path [3,1,3] - max is 3, node.val is 3 ✓
- Node 1: Path [3,4,1] - max is 4, node.val is 1 ✗
- Node 5: Path [3,4,5] - max is 5, node.val is 5 ✓
```

### Example 2
```
Input: root = [3,3,null,4,2]
        3
       /
      3
     / \
    4   2

Output: 3
Explanation: Good nodes are: 3 (root), 3, and 4.
- Node 2 is not good because max in path [3,3,2] is 3
```

### Example 3
```
Input: root = [1]
Output: 1
Explanation: Root is always a good node.
```

## Constraints

- The number of nodes in the binary tree is in the range `[1, 10^5]`.
- `-10^4 <= Node.val <= 10^4`

## Solution Approaches

### Approach 1: Recursive DFS
```python
def goodNodes(root):
    def dfs(node, max_val):
        if not node:
            return 0
        
        # Check if current node is good
        count = 1 if node.val >= max_val else 0
        
        # Update max value for children
        new_max = max(max_val, node.val)
        
        # Recurse for children
        count += dfs(node.left, new_max)
        count += dfs(node.right, new_max)
        
        return count
    
    return dfs(root, float('-inf'))
```

### Approach 2: Iterative DFS with Stack
```python
def goodNodes(root):
    if not root:
        return 0
    
    count = 0
    stack = [(root, float('-inf'))]  # (node, max_value_in_path)
    
    while stack:
        node, max_val = stack.pop()
        
        if node.val >= max_val:
            count += 1
        
        new_max = max(max_val, node.val)
        
        if node.left:
            stack.append((node.left, new_max))
        if node.right:
            stack.append((node.right, new_max))
    
    return count
```

### Approach 3: Iterative BFS with Queue
```python
from collections import deque

def goodNodes(root):
    if not root:
        return 0
    
    count = 0
    queue = deque([(root, float('-inf'))])
    
    while queue:
        node, max_val = queue.popleft()
        
        if node.val >= max_val:
            count += 1
        
        new_max = max(max_val, node.val)
        
        if node.left:
            queue.append((node.left, new_max))
        if node.right:
            queue.append((node.right, new_max))
    
    return count
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative DFS | O(n) | O(h) - explicit stack |
| Iterative BFS | O(n) | O(w) - queue width |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Track maximum**: Keep track of maximum value seen in the path from root
- **Good node condition**: `node.val >= max_value_in_path`
- **Update maximum**: Pass updated maximum to children

## Visual Explanation

```
Tree:
          3              Path analysis:
         / \             Root: max=-inf, 3 >= -inf ✓ (count=1)
        1   4           Node 1: max=3, 1 < 3 ✗
       /   / \          Node 4: max=3, 4 >= 3 ✓ (count=2)
      3   1   5         Node 3: max=3, 3 >= 3 ✓ (count=3)
                        Node 1: max=4, 1 < 4 ✗
                        Node 5: max=4, 5 >= 4 ✓ (count=4)

Total good nodes: 4
```

## Algorithm Steps

1. Start DFS/BFS from root with `max_val = -infinity`
2. For each node:
   - If `node.val >= max_val`, it's a good node (increment count)
   - Update `max_val = max(max_val, node.val)`
   - Pass updated `max_val` to children
3. Return total count

## Related Problems

- [Path Sum](problems/09_path_sum.md) - Check path sums
- [Binary Tree Paths](problems/10_binary_tree_paths.md) - Find all paths
- [Maximum Depth of Binary Tree](problems/04_maximum_depth_of_binary_tree.md)