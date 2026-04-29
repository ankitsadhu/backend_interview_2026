# Binary Tree Postorder Traversal

## Question

Given the `root` of a binary tree, return the postorder traversal of its nodes' values.

**Postorder Traversal**: Visit left subtree, then right subtree, then root (Left → Right → Root)

## Examples

### Example 1
```
Input: root = [1,null,2,3]
       1
        \
         2
        /
       3

Output: [3,2,1]
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

Output: [6,7,4,5,2,9,8,3,1]
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

- Can you solve this iteratively? (Hint: Use two stacks or a modified preorder approach)

## Solution Approaches

### Approach 1: Recursive DFS
```python
def postorderTraversal(root):
    result = []
    
    def dfs(node):
        if not node:
            return
        dfs(node.left)
        dfs(node.right)
        result.append(node.val)
    
    dfs(root)
    return result
```

### Approach 2: Iterative with Two Stacks
```python
def postorderTraversal(root):
    if not root:
        return []
    
    stack1 = [root]
    stack2 = []
    result = []
    
    while stack1:
        node = stack1.pop()
        stack2.append(node)
        if node.left:
            stack1.append(node.left)
        if node.right:
            stack1.append(node.right)
    
    while stack2:
        result.append(stack2.pop().val)
    
    return result
```

### Approach 3: Iterative with One Stack (Modified Preorder)
```python
def postorderTraversal(root):
    if not root:
        return []
    
    result = []
    stack = [root]
    
    while stack:
        node = stack.pop()
        result.append(node.val)
        # Push left first so right is processed first
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    
    # Reverse to get postorder
    return result[::-1]
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(n) | O(h) - recursion stack |
| Two Stacks | O(n) | O(h) - explicit stacks |
| One Stack | O(n) | O(h) - explicit stack |

Where n = number of nodes, h = height of tree

## Applications

- **Deleting a tree**: Postorder traversal is used to delete nodes from bottom up
- **Postfix notation**: Used in expression trees to generate postfix (Reverse Polish) notation
- **Tree size calculation**: Calculate size/height of tree before processing root