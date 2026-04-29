# Path Sum II

## Question

Given the `root` of a binary tree and an integer `targetSum`, return all **root-to-leaf** paths where the sum of the node values in the path equals `targetSum`. Each path should be returned as a list of node values.

A **leaf** is a node with no children.

## Examples

### Example 1
```
Input: root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
              5
             / \
            4   8
           /   / \
          11  13  4
         /  \    / \
        7    2  5   1

Output: [[5,4,11,2], [5,8,4,5]]
Explanation: Two paths sum to 22:
- 5 + 4 + 11 + 2 = 22
- 5 + 8 + 4 + 5 = 22
```

### Example 2
```
Input: root = [1,2,3], targetSum = 5
       1
      / \
     2   3

Output: []
Explanation: No path sums to 5
```

### Example 3
```
Input: root = [1,2], targetSum = 0
       1
      /
     2

Output: []
```

## Constraints

- The number of nodes in the tree is in the range `[0, 5000]`.
- `-1000 <= Node.val <= 1000`
- `-1000 <= targetSum <= 1000`

## Solution Approaches

### Approach 1: Recursive DFS with Backtracking
```python
def pathSum(root, targetSum):
    result = []
    
    def dfs(node, target, path):
        if not node:
            return
        
        path.append(node.val)
        
        # Check if leaf and sum matches
        if not node.left and not node.right and target == node.val:
            result.append(list(path))  # Make a copy
        
        # Recurse for children
        dfs(node.left, target - node.val, path)
        dfs(node.right, target - node.val, path)
        
        # Backtrack
        path.pop()
    
    dfs(root, targetSum, [])
    return result
```

### Approach 2: Iterative DFS with Stack
```python
def pathSum(root, targetSum):
    if not root:
        return []
    
    result = []
    stack = [(root, targetSum - root.val, [root.val])]
    
    while stack:
        node, remaining, path = stack.pop()
        
        # Check if leaf and sum matches
        if not node.left and not node.right and remaining == 0:
            result.append(path)
        
        if node.right:
            stack.append((node.right, remaining - node.right.val, path + [node.right.val]))
        if node.left:
            stack.append((node.left, remaining - node.left.val, path + [node.left.val]))
    
    return result
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n^2) | O(h) - recursion + path |
| Iterative DFS | O(n^2) | O(h) - stack + paths |

Where n = number of nodes, h = height of tree

## Key Insights

- **Backtracking**: Add node to path, recurse, then remove
- **Copy path**: When adding to result, make a copy of the path
- **Leaf check**: Only add path when at a leaf node

## Visual Explanation

```
Tree with targetSum = 22:
              5
             / \
            4   8
           /   / \
          11  13  4
         /  \    / \
        7    2  5   1

Paths explored:
[5,4,11,7] -> sum=27 ✗
[5,4,11,2] -> sum=22 ✓ -> Add to result
[5,8,13] -> sum=26 ✗
[5,8,4,5] -> sum=22 ✓ -> Add to result
[5,8,4,1] -> sum=18 ✗

Result: [[5,4,11,2], [5,8,4,5]]
```

## Algorithm Steps

1. Start DFS from root with empty path
2. Add current node to path
3. If leaf and path sum equals target, add copy of path to result
4. Recurse for left and right children with updated target
5. Remove current node from path (backtrack)
6. Return all valid paths

## Related Problems

- [Path Sum](problems/09_path_sum.md) - Check if any path exists
- [Path Sum III](problems/34_path_sum_iii.md) - Paths can start from any node
- [Binary Tree Paths](problems/10_binary_tree_paths.md) - Return all paths