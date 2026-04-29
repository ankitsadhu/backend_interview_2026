# Symmetric Tree

## Question

Given the `root` of a binary tree, check whether it is a **mirror of itself** (i.e., symmetric around its center).

A binary tree is symmetric if you can draw a vertical line through the root node and then reverse the right subtree, it will be identical to the left subtree.

## Examples

### Example 1
```
Input: root = [1,2,2,3,4,4,3]
          1
        /   \
       2     2
      / \   / \
     3   4 4   3

Output: true
```

### Example 2
```
Input: root = [1,2,2,null,3,null,3]
          1
        /   \
       2     2
        \     \
         3     3

Output: false
Explanation: The right subtree of left node and left subtree of right node are not mirrors
```

### Example 3
```
Input: root = [1]
Output: true
```

### Example 4
```
Input: root = []
Output: true
```

## Constraints

- The number of nodes in the tree is in the range `[1, 1000]`.
- `-100 <= Node.val <= 100`

## Solution Approaches

### Approach 1: Recursive DFS
```python
def isSymmetric(root):
    def isMirror(t1, t2):
        # Both None - symmetric
        if not t1 and not t2:
            return True
        
        # One is None - not symmetric
        if not t1 or not t2:
            return False
        
        # Values must be equal
        if t1.val != t2.val:
            return False
        
        # Check: left of t1 with right of t2, and right of t1 with left of t2
        return isMirror(t1.left, t2.right) and isMirror(t1.right, t2.left)
    
    return isMirror(root.left, root.right)
```

### Approach 2: Iterative BFS (Queue)
```python
from collections import deque

def isSymmetric(root):
    if not root:
        return True
    
    queue = deque([(root.left, root.right)])
    
    while queue:
        t1, t2 = queue.popleft()
        
        if not t1 and not t2:
            continue
        
        if not t1 or not t2:
            return False
        
        if t1.val != t2.val:
            return False
        
        # Add mirrored pairs
        queue.append((t1.left, t2.right))
        queue.append((t1.right, t2.left))
    
    return True
```

### Approach 3: Iterative DFS (Stack)
```python
def isSymmetric(root):
    if not root:
        return True
    
    stack = [(root.left, root.right)]
    
    while stack:
        t1, t2 = stack.pop()
        
        if not t1 and not t2:
            continue
        
        if not t1 or not t2:
            return False
        
        if t1.val != t2.val:
            return False
        
        stack.append((t1.left, t2.right))
        stack.append((t1.right, t2.left))
    
    return True
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative BFS | O(n) | O(w) - queue width |
| Iterative DFS | O(n) | O(h) - explicit stack |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Mirror comparison**: Compare left subtree with mirror of right subtree
- **Pair checking**: Always compare `t1.left` with `t2.right` and `t1.right` with `t2.left`
- **Base case**: Empty tree is symmetric

## Visual Explanation

```
For tree to be symmetric:
         1
       /   \
      2     2    <- These must be mirrors
     / \   / \
    3   4 4   3  <- These pairs must match

Mirror pairs:
- (2, 2) - root's children
- (3, 3) - outer nodes
- (4, 4) - inner nodes
```

## Related Problems

- [Same Tree](problems/06_same_tree.md) - Check if two trees are identical
- [Subtree of Another Tree](problems/29_subtree_of_another_tree.md) - Check if one tree is subtree of another