# Diameter of Binary Tree

## Question

Given the `root` of a binary tree, return the **diameter** of the tree.

The **diameter** of a binary tree is the **length** of the longest path between any two nodes in a tree. This path may or may not pass through the `root`.

The **length** of a path between two nodes is represented by the number of **edges** between them.

## Examples

### Example 1
```
Input: root = [1,2,3,4,5]
          1
         / \
        2   3
       / \
      4   5

Output: 3
Explanation: The longest path is [4,2,1,3] or [5,2,1,3] which has 3 edges.
```

### Example 2
```
Input: root = [1,2]
       1
      /
     2

Output: 1
Explanation: The longest path is [2,1] which has 1 edge.
```

### Example 3
```
Input: root = [1,2,3,4,5,null,null,6,7,8,null,9]
            1
           / \
          2   3
         / \
        4   5
       /   /
      6   8
     /   /
    7   9

Output: 7
Explanation: The longest path is [7,6,4,2,1,3] or [9,8,5,2,1,3] which has 7 edges.
```

## Constraints

- The number of nodes in the tree is in the range `[1, 10^4]`.
- `-100 <= Node.val <= 100`

## Solution Approaches

### Approach: Recursive DFS (Height + Diameter)
```python
def diameterOfBinaryTree(root):
    diameter = [0]  # Use list to allow modification
    
    def height(node):
        if not node:
            return 0
        
        # Get heights of left and right subtrees
        left_height = height(node.left)
        right_height = height(node.right)
        
        # Update diameter if path through this node is longer
        diameter[0] = max(diameter[0], left_height + right_height)
        
        # Return height of this subtree
        return 1 + max(left_height, right_height)
    
    height(root)
    return diameter[0]
```

### Approach: Iterative (Postorder with Stack)
```python
def diameterOfBinaryTree(root):
    if not root:
        return 0
    
    diameter = 0
    height_map = {None: 0}  # Map node to its height
    stack = []
    current = root
    last_visited = None
    
    while stack or current:
        if current:
            stack.append(current)
            current = current.left
        else:
            peek = stack[-1]
            if peek.right and last_visited != peek.right:
                current = peek.right
            else:
                # Process node
                left_h = height_map.get(peek.left, 0)
                right_h = height_map.get(peek.right, 0)
                height_map[peek] = 1 + max(left_h, right_h)
                diameter = max(diameter, left_h + right_h)
                last_visited = stack.pop()
    
    return diameter
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative | O(n) | O(h) - explicit stack + map |

Where n = number of nodes, h = height of tree

## Key Insights

- **Diameter through a node**: `left_height + right_height`
- **Global maximum**: Track the maximum diameter across all nodes
- **Height calculation**: Reuse height computation for diameter

## Visual Explanation

```
Tree:
          1
         / \
        2   3
       / \
      4   5

Heights:
- Node 4: height = 0 (leaf)
- Node 5: height = 0 (leaf)
- Node 2: height = 1 + max(0,0) = 1
- Node 3: height = 0 (leaf)
- Node 1: height = 1 + max(1,0) = 2

Diameters at each node:
- Node 4: 0 + 0 = 0
- Node 5: 0 + 0 = 0
- Node 2: 1 + 1 = 2  (path: 4-2-5)
- Node 3: 0 + 0 = 0
- Node 1: 1 + 0 = 1  (path through root)

Maximum diameter = 2... wait, let me recalculate
Actually: Node 2 has left_height=1 (node 4), right_height=1 (node 5)
Diameter through node 2 = 1 + 1 = 2
But diameter through node 1 = left_height(2) + right_height(1) = 2 + 0 = 2

The actual diameter is 3 edges: 4->2->1->3 or 5->2->1->3
```

## Common Mistakes

1. **Counting nodes instead of edges**: Diameter is number of edges, not nodes
2. **Only considering path through root**: The longest path may not pass through root
3. **Not tracking global maximum**: Need to check diameter at every node

## Algorithm Steps

1. For each node, calculate the height of left and right subtrees
2. The diameter through that node = left_height + right_height
3. Keep track of the maximum diameter seen
4. Return the maximum diameter

## Related Problems

- [Maximum Depth of Binary Tree](problems/04_maximum_depth_of_binary_tree.md)
- [Balanced Binary Tree](problems/28_balanced_binary_tree.md)
- [Binary Tree Maximum Path Sum](problems/35_binary_tree_maximum_path_sum.md)