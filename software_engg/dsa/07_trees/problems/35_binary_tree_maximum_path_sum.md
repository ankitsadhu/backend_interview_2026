# Binary Tree Maximum Path Sum

## Question

A **path** in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. A node can only appear in the sequence **at most once**. Note that the path does not need to pass through the root.

The **path sum** is the sum of the node's values in the path.

Given the `root` of a binary tree, return the maximum **path sum** of any **non-empty** path.

## Examples

### Example 1
```
Input: root = [1,2,3]
       1
      / \
     2   3

Output: 6
Explanation: The optimal path is 2 -> 1 -> 3 with a path sum of 2 + 1 + 3 = 6.
```

### Example 2
```
Input: root = [-10,9,20,null,null,15,7]
        -10
        /  \
       9   20
           / \
          15  7

Output: 42
Explanation: The optimal path is 15 -> 20 -> 7 with a path sum of 15 + 20 + 7 = 42.
```

### Example 3
```
Input: root = [-3]
Output: -3
```

## Constraints

- The number of nodes in the tree is in the range `[1, 3 * 10^4]`.
- `-1000 <= Node.val <= 1000`

## Solution Approaches

### Approach: Recursive DFS (Postorder)
```python
def maxPathSum(root):
    max_sum = [float('-inf')]
    
    def max_gain(node):
        if not node:
            return 0
        
        # Get max gain from left and right subtrees
        # If gain is negative, don't include that subtree (take 0)
        left_gain = max(max_gain(node.left), 0)
        right_gain = max(max_gain(node.right), 0)
        
        # Calculate path sum through current node (can use both children)
        price_newpath = node.val + left_gain + right_gain
        
        # Update global maximum
        max_sum[0] = max(max_sum[0], price_newpath)
        
        # Return max gain if continuing the same path (only one child)
        return node.val + max(left_gain, right_gain)
    
    max_gain(root)
    return max_sum[0]
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |

Where n = number of nodes, h = height of tree

## Key Insights

- **Two types of paths**: 
  1. Path through node (can use both children) - for updating max
  2. Path continuing from node (only one child) - for returning
- **Negative handling**: If subtree gain is negative, don't include it
- **Global maximum**: Track the maximum path sum across all nodes

## Visual Explanation

```
Tree:
        -10
        /  \
       9   20
           / \
          15  7

For node 20:
- left_gain = max(max_gain(15), 0) = 15
- right_gain = max(max_gain(7), 0) = 7
- price_newpath = 20 + 15 + 7 = 42  <- This is the max path sum
- return 20 + max(15, 7) = 35  <- Max gain if continuing through 20

For node -10:
- left_gain = max(max_gain(9), 0) = 9
- right_gain = max(max_gain(20), 0) = 35
- price_newpath = -10 + 9 + 35 = 34
- return -10 + max(9, 35) = 25

Global max = max(42, 34, ...) = 42
```

## Algorithm Steps

1. For each node, calculate the maximum gain from left and right subtrees
2. If gain is negative, treat it as 0 (don't include that subtree)
3. Calculate the path sum if we use both subtrees (new path through this node)
4. Update global maximum if this path is better
5. Return the maximum gain if we continue the path through this node (only one subtree)

## Why This Works?

- **Path through node**: `node.val + left_gain + right_gain` - This is a complete path
- **Return value**: `node.val + max(left_gain, right_gain)` - This can be extended upward

## Common Mistakes

1. **Only considering paths through root**: The max path may not include root
2. **Not handling negative values**: Negative subtrees should be excluded
3. **Confusing path types**: Path for max vs path for return are different

## Related Problems

- [Diameter of Binary Tree](problems/27_diameter_of_binary_tree.md) - Similar pattern
- [Path Sum](problems/09_path_sum.md) - Simpler path sum problem
- [Maximum Subarray](problems/) - 1D version of this problem