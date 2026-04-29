# Binary Tree Preorder Traversal

## Question

Given the `root` of a binary tree, return the preorder traversal of its nodes' values.

**Preorder Traversal**: Visit root, then left subtree, then right subtree (Root → Left → Right)

## Examples

### Example 1
```
Input: root = [1,null,2,3]
       1
        \
         2
        /
       3

Output: [1,2,3]
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

Output: [1,2,4,5,6,7,3,8,9]
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
def preorderTraversal(root):
    result = []
    
    def dfs(node):
        if not node:
            return
        result.append(node.val)
        dfs(node.left)
        dfs(node.right)
    
    dfs(root)
    return result
```

### Approach 2: Iterative with Stack
```python
def preorderTraversal(root):
    if not root:
        return []
    
    result = []
    stack = [root]
    
    while stack:
        node = stack.pop()
        result.append(node.val)
        # Push right first so left is processed first
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    
    return result
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(n) | O(h) - recursion stack |
| Iterative | O(n) | O(h) - explicit stack |

Where n = number of nodes, h = height of tree

## Applications

- **Copying a tree**: Preorder traversal creates a copy of the tree structure
- **Prefix notation**: Used in expression trees to generate prefix expressions
- **Serialization**: Often used to serialize tree structure