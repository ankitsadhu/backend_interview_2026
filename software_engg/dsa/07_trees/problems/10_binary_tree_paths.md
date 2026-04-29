# Binary Tree Paths

## Question

Given the `root` of a binary tree, return all root-to-leaf paths in **any order**.

A **leaf** is a node with no children.

## Examples

### Example 1
```
Input: root = [1,2,3,null,5]
       1
      / \
     2   3
      \
       5

Output: ["1->2->5", "1->3"]
```

### Example 2
```
Input: root = [1]
       1

Output: ["1"]
```

### Example 3
```
Input: root = [1,2,3,4,5]
          1
         / \
        2   3
       / \
      4   5

Output: ["1->2->4", "1->2->5", "1->3"]
```

### Example 4
```
Input: root = []
Output: []
```

## Constraints

- The number of nodes in the tree is in the range `[0, 100]`.
- `-100 <= Node.val <= 100`

## Solution Approaches

### Approach 1: Recursive DFS (Backtracking)
```python
def binaryTreePaths(root):
    result = []
    
    def dfs(node, path):
        if not node:
            return
        
        # Add current node to path
        path.append(str(node.val))
        
        # If leaf, add path to result
        if not node.left and not node.right:
            result.append("->".join(path))
        else:
            # Continue exploring
            dfs(node.left, path)
            dfs(node.right, path)
        
        # Backtrack
        path.pop()
    
    dfs(root, [])
    return result
```

### Approach 2: Recursive DFS (String Building)
```python
def binaryTreePaths(root):
    result = []
    
    def dfs(node, path):
        if not node:
            return
        
        # Build path string
        if path:
            path += "->" + str(node.val)
        else:
            path = str(node.val)
        
        # If leaf, add to result
        if not node.left and not node.right:
            result.append(path)
            return
        
        dfs(node.left, path)
        dfs(node.right, path)
    
    dfs(root, "")
    return result
```

### Approach 3: Iterative DFS with Stack
```python
def binaryTreePaths(root):
    if not root:
        return []
    
    result = []
    stack = [(root, str(root.val))]
    
    while stack:
        node, path = stack.pop()
        
        # If leaf, add to result
        if not node.left and not node.right:
            result.append(path)
        
        if node.right:
            stack.append((node.right, path + "->" + str(node.right.val)))
        if node.left:
            stack.append((node.left, path + "->" + str(node.left.val)))
    
    return result
```

### Approach 4: Iterative BFS with Queue
```python
from collections import deque

def binaryTreePaths(root):
    if not root:
        return []
    
    result = []
    queue = deque([(root, str(root.val))])
    
    while queue:
        node, path = queue.popleft()
        
        # If leaf, add to result
        if not node.left and not node.right:
            result.append(path)
        
        if node.left:
            queue.append((node.left, path + "->" + str(node.left.val)))
        if node.right:
            queue.append((node.right, path + "->" + str(node.right.val)))
    
    return result
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n * h) | O(h) - recursion + path |
| Iterative DFS | O(n * h) | O(h) - stack + path |
| Iterative BFS | O(n * h) | O(w * h) - queue stores paths |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Path building**: Build path string as we traverse down
- **Leaf detection**: Only add path when we reach a leaf node
- **String format**: Use "->" to separate node values
- **Backtracking**: When using list for path, remember to pop after exploring

## Variations

1. **Return as list of lists**: Instead of strings, return `[[1,2,5], [1,3]]`
2. **Sum of all paths**: Calculate sum of all root-to-leaf numbers
3. **Path with conditions**: Find paths where sum equals target

## Related Problems

- [Path Sum](problems/09_path_sum.md) - Check if any path sums to target
- [Path Sum II](problems/33_path_sum_ii.md) - Find all paths that sum to target
- [Sum Root to Leaf Numbers](problems/11_sum_root_to_leaf_numbers.md) - Calculate numeric sum of paths