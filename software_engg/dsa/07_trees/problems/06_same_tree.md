# Same Tree

## Question

Given the roots of two binary trees `p` and `q`, check if they are the same, or not.

Two binary trees are considered the same if they are **structurally identical**, and the nodes have the **same value**.

## Examples

### Example 1
```
Input: p = [1,2,3], q = [1,2,3]
       1              1
      / \            / \
     2   3          2   3

Output: true
```

### Example 2
```
Input: p = [1,2], q = [1,null,2]
       1              1
      /                \
     2                  2

Output: false
Explanation: Trees are not structurally identical
```

### Example 3
```
Input: p = [1,2,1], q = [1,1,2]
       1              1
      / \            / \
     2   1          1   2

Output: false
Explanation: Trees are structurally identical but nodes have different values
```

### Example 4
```
Input: p = [], q = []
Output: true
```

## Constraints

- The number of nodes in both trees is in the range `[0, 100]`.
- `-10^4 <= Node.val <= 10^4`

## Solution Approaches

### Approach 1: Recursive DFS
```python
def isSameTree(p, q):
    # Both None - same
    if not p and not q:
        return True
    
    # One is None - different
    if not p or not q:
        return False
    
    # Values must be equal
    if p.val != q.val:
        return False
    
    # Recursively check left and right subtrees
    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)
```

### Approach 2: Iterative BFS
```python
from collections import deque

def isSameTree(p, q):
    def check(p, q):
        if not p and not q:
            return True
        if not p or not q:
            return False
        if p.val != q.val:
            return False
        return True
    
    queue = deque([(p, q)])
    
    while queue:
        node1, node2 = queue.popleft()
        
        if not check(node1, node2):
            return False
        
        if node1 and node2:
            queue.append((node1.left, node2.left))
            queue.append((node1.right, node2.right))
    
    return True
```

### Approach 3: Iterative DFS
```python
def isSameTree(p, q):
    stack = [(p, q)]
    
    while stack:
        node1, node2 = stack.pop()
        
        if not node1 and not node2:
            continue
        if not node1 or not node2:
            return False
        if node1.val != node2.val:
            return False
        
        stack.append((node1.left, node2.left))
        stack.append((node1.right, node2.right))
    
    return True
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(min(n, m)) | O(min(h1, h2)) - recursion |
| Iterative BFS | O(min(n, m)) | O(min(w1, w2)) - queue |
| Iterative DFS | O(min(n, m)) | O(min(h1, h2)) - stack |

Where n, m = number of nodes in each tree, h = height, w = width

## Key Insights

- **Base cases**: Handle null nodes carefully
- **Short-circuit**: Return false as soon as a difference is found
- **Structural check**: Both structure and values must match

## Related Problems

- [Symmetric Tree](problems/07_symmetric_tree.md) - Check if tree is mirror of itself
- [Subtree of Another Tree](problems/29_subtree_of_another_tree.md) - Check if one tree is subtree of another