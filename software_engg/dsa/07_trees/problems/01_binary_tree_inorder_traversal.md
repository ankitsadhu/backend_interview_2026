# Binary Tree Inorder Traversal

## Question

Given the `root` of a binary tree, return the inorder traversal of its nodes' values.

**Inorder Traversal**: Visit left subtree, then root, then right subtree (Left → Root → Right)

## Examples

### Example 1
```
Input: root = [1,null,2,3]
       1
        \
         2
        /
       3

Output: [1,3,2]
```

### Example 2
```
Input: root = [1,2,3,4,5,null,8,null,null,6,7,9]
          1
        /   \
       2     3
      / \     \
     4   5     8
        / \   /
       6   7 9

Output: [4,2,6,5,7,1,3,9,8]
```

### Example 3
```
Input: root = []
Output: []
```

### Example 4
```
Input: root = [1]
Output: [1]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 100]`.
- `-100 <= Node.val <= 100`

## Follow-up

- Can you solve this iteratively? (Hint: Use a stack)

## Solution Approaches

### Approach 1: Recursive DFS
```python
def inorderTraversal(root):
    result = []
    
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        result.append(node.val)
        dfs(node.right)
    
    dfs(root)
    return result
```

### Approach 2: Iterative with Stack
```python
def inorderTraversal(root):
    result = []
    stack = []
    current = root
    
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    
    return result
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(n) | O(h) - recursion stack |
| Iterative | O(n) | O(h) - explicit stack |

Where n = number of nodes, h = height of tree