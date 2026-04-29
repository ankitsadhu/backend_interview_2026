# Path Sum

## Question

Given the `root` of a binary tree and an integer `targetSum`, return `true` if the tree has a **root-to-leaf** path such that adding up all the values along the path equals `targetSum`.

A **leaf** is a node with no children.

## Examples

### Example 1
```
Input: root = [5,4,8,11,null,13,4,7,2,null,null,null,1], targetSum = 22
              5
             / \
            4   8
           /   / \
          11  13  4
         /  \      \
        7    2      1

Output: true
Explanation: The root-to-leaf path 5 -> 4 -> 11 -> 2 sums to 22
```

### Example 2
```
Input: root = [1,2,3], targetSum = 5
       1
      / \
     2   3

Output: false
Explanation: No root-to-leaf path sums to 5
```

### Example 3
```
Input: root = [], targetSum = 0
Output: false
Explanation: Empty tree has no paths
```

### Example 4
```
Input: root = [1,2], targetSum = 1
       1
      /
     2

Output: false
Explanation: The only path is 1 -> 2 = 3, not 1
```

## Constraints

- The number of nodes in the tree is in the range `[0, 5000]`.
- `-1000 <= Node.val <= 1000`
- `-1000 <= targetSum <= 1000`

## Solution Approaches

### Approach 1: Recursive DFS
```python
def hasPathSum(root, targetSum):
    if not root:
        return False
    
    # Check if we're at a leaf node
    if not root.left and not root.right:
        return targetSum == root.val
    
    # Recursively check left and right subtrees
    remaining = targetSum - root.val
    return hasPathSum(root.left, remaining) or hasPathSum(root.right, remaining)
```

### Approach 2: Iterative DFS with Stack
```python
def hasPathSum(root, targetSum):
    if not root:
        return False
    
    stack = [(root, targetSum - root.val)]
    
    while stack:
        node, current_sum = stack.pop()
        
        # Check if we're at a leaf and sum matches
        if not node.left and not node.right and current_sum == 0:
            return True
        
        if node.right:
            stack.append((node.right, current_sum - node.right.val))
        if node.left:
            stack.append((node.left, current_sum - node.left.val))
    
    return False
```

### Approach 3: Iterative BFS with Queue
```python
from collections import deque

def hasPathSum(root, targetSum):
    if not root:
        return False
    
    queue = deque([(root, targetSum - root.val)])
    
    while queue:
        node, current_sum = queue.popleft()
        
        # Check if we're at a leaf and sum matches
        if not node.left and not node.right and current_sum == 0:
            return True
        
        if node.left:
            queue.append((node.left, current_sum - node.left.val))
        if node.right:
            queue.append((node.right, current_sum - node.right.val))
    
    return False
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative DFS | O(n) | O(h) - explicit stack |
| Iterative BFS | O(n) | O(w) - queue width |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Must be root-to-leaf**: Path must start at root and end at a leaf node
- **Leaf definition**: A leaf has no children (both left and right are None)
- **Subtract approach**: Subtract node value from target as we traverse down
- **Early termination**: Can return true as soon as a valid path is found

## Common Mistakes

1. **Not checking for leaf**: Must verify both children are None
2. **Empty tree**: Empty tree should return false
3. **Single node tree**: Root is also a leaf if it has no children

## Related Problems

- [Path Sum II](problems/33_path_sum_ii.md) - Find all paths that sum to target
- [Path Sum III](problems/34_path_sum_iii.md) - Paths can start from any node
- [Sum Root to Leaf Numbers](problems/11_sum_root_to_leaf_numbers.md) - Build numbers from paths