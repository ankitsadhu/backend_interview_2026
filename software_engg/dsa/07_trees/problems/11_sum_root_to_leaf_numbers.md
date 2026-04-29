# Sum Root to Leaf Numbers

## Question

You are given the `root` of a binary tree containing digits from `0` to `9` only.

Each root-to-leaf path in the tree represents a **number**.

For example, the root-to-leaf path `1 -> 2 -> 3` represents the number `123`.

Return the **total sum** of all root-to-leaf numbers.

A **leaf** node is a node with no children.

## Examples

### Example 1
```
Input: root = [1,2,3]
       1
      / \
     2   3

Output: 25
Explanation:
- Path 1->2 represents number 12
- Path 1->3 represents number 13
- Total sum = 12 + 13 = 25
```

### Example 2
```
Input: root = [4,9,0,5,1]
        4
       / \
      9   0
     / \
    5   1

Output: 1026
Explanation:
- Path 4->9->5 represents number 495
- Path 4->9->1 represents number 491
- Path 4->0 represents number 40
- Total sum = 495 + 491 + 40 = 1026
```

### Example 3
```
Input: root = [0]
Output: 0
```

## Constraints

- The number of nodes in the tree is in the range `[1, 1000]`.
- `0 <= Node.val <= 9`
- The depth of the tree will not exceed `10`.

## Solution Approaches

### Approach 1: Recursive DFS
```python
def sumNumbers(root):
    def dfs(node, current_num):
        if not node:
            return 0
        
        # Build the number by appending current digit
        current_num = current_num * 10 + node.val
        
        # If leaf, return the number
        if not node.left and not node.right:
            return current_num
        
        # Sum from both subtrees
        return dfs(node.left, current_num) + dfs(node.right, current_num)
    
    return dfs(root, 0)
```

### Approach 2: Iterative DFS with Stack
```python
def sumNumbers(root):
    if not root:
        return 0
    
    total = 0
    stack = [(root, 0)]
    
    while stack:
        node, current_num = stack.pop()
        
        # Build the number
        current_num = current_num * 10 + node.val
        
        # If leaf, add to total
        if not node.left and not node.right:
            total += current_num
        
        if node.right:
            stack.append((node.right, current_num))
        if node.left:
            stack.append((node.left, current_num))
    
    return total
```

### Approach 3: Iterative BFS with Queue
```python
from collections import deque

def sumNumbers(root):
    if not root:
        return 0
    
    total = 0
    queue = deque([(root, 0)])
    
    while queue:
        node, current_num = queue.popleft()
        
        # Build the number
        current_num = current_num * 10 + node.val
        
        # If leaf, add to total
        if not node.left and not node.right:
            total += current_num
        
        if node.left:
            queue.append((node.left, current_num))
        if node.right:
            queue.append((node.right, current_num))
    
    return total
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative DFS | O(n) | O(h) - explicit stack |
| Iterative BFS | O(n) | O(w) - queue width |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Number building**: `current_num = current_num * 10 + node.val` builds the number digit by digit
- **Leaf check**: Only add to sum when reaching a leaf node
- **Divide and conquer**: Sum from left and right subtrees can be computed independently

## Mathematical Explanation

For a path like `4 -> 9 -> 5`:
```
Step 1: current = 0 * 10 + 4 = 4
Step 2: current = 4 * 10 + 9 = 49
Step 3: current = 49 * 10 + 5 = 495
```

## Related Problems

- [Path Sum](problems/09_path_sum.md) - Check if any path sums to target
- [Path Sum II](problems/33_path_sum_ii.md) - Find all paths that sum to target
- [Binary Tree Paths](problems/10_binary_tree_paths.md) - Return all paths as strings