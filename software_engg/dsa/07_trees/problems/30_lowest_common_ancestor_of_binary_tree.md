# Lowest Common Ancestor of a Binary Tree

## Question

Given a binary tree, find the lowest common ancestor (LCA) of two given nodes, `p` and `q`.

The **lowest common ancestor** is defined between two nodes `p` and `q` as the lowest node in the tree that has both `p` and `q` as descendants (where we allow a node to be a descendant of itself).

**Note**: The tree is NOT necessarily a binary search tree.

## Examples

### Example 1
```
Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1
              3
            /   \
           5     1
          / \   / \
         6   2 0   8
            / \
           7   4

Output: 3
Explanation: The LCA of nodes 5 and 1 is 3.
```

### Example 2
```
Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4
              3
            /   \
           5     1
          / \   / \
         6   2 0   8
            / \
           7   4

Output: 5
Explanation: The LCA of nodes 5 and 4 is 5, since a node can be a descendant of itself.
```

### Example 3
```
Input: root = [1,2], p = 1, q = 2
       1
      /
     2

Output: 1
```

## Constraints

- The number of nodes in the tree is in the range `[2, 10^5]`.
- `-10^9 <= Node.val <= 10^9`
- All `Node.val` are unique.
- `p != q`
- `p` and `q` will exist in the tree.

## Solution Approaches

### Approach 1: Recursive DFS
```python
def lowestCommonAncestor(root, p, q):
    if not root:
        return None
    
    # If current node is p or q, return it
    if root == p or root == q:
        return root
    
    # Search in left and right subtrees
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    
    # If both left and right are found, current node is LCA
    if left and right:
        return root
    
    # Return the non-null result
    return left if left else right
```

### Approach 2: Iterative with Parent Pointers
```python
def lowestCommonAncestor(root, p, q):
    # Build parent map using BFS
    parent = {root: None}
    stack = [root]
    
    while p not in parent or q not in parent:
        node = stack.pop()
        if node.left:
            parent[node.left] = node
            stack.append(node.left)
        if node.right:
            parent[node.right] = node
            stack.append(node.right)
    
    # Collect all ancestors of p
    ancestors = set()
    while p:
        ancestors.add(p)
        p = parent[p]
    
    # Find first ancestor of q that's in ancestors
    while q not in ancestors:
        q = parent[q]
    
    return q
```

### Approach 3: Iterative with Stack (Postorder)
```python
def lowestCommonAncestor(root, p, q):
    stack = [root]
    parent = {root: None}
    
    # Find p and q
    while p not in parent and q not in parent:
        node = stack.pop()
        if node.left:
            parent[node.left] = node
            stack.append(node.left)
        if node.right:
            parent[node.right] = node
            stack.append(node.right)
    
    # Trace path from p to root
    ancestors = set()
    while p:
        ancestors.add(p)
        p = parent[p]
    
    # Find first common ancestor
    while q not in ancestors:
        q = parent[q]
    
    return q
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive DFS | O(n) | O(h) - recursion stack |
| Iterative with parent | O(n) | O(n) - parent map |
| Iterative with stack | O(n) | O(n) - stack + parent |

Where n = number of nodes, h = height of tree

## Key Insights

- **No BST property**: Cannot use value comparison to navigate
- **Bottom-up approach**: Recurse first, then check results
- **Self as ancestor**: A node can be its own ancestor

## Visual Explanation

```
Find LCA of 5 and 1:
              3
            /   \
           5     1
          / \   / \
         6   2 0   8
            / \
           7   4

Recursive calls:
- LCA(3): left=LCA(5)=5, right=LCA(1)=1 -> both found, return 3

Find LCA of 5 and 4:
- LCA(3): left=LCA(5)=5, right=LCA(1)=null -> return 5
- LCA(5): left=LCA(6)=null, right=LCA(2)=4 -> but 5==p, return 5
```

## Algorithm Steps (Recursive)

1. If root is null, return null
2. If root is p or q, return root
3. Recursively search for LCA in left subtree
4. Recursively search for LCA in right subtree
5. If both left and right return non-null, root is LCA
6. Otherwise, return the non-null result

## Difference from BST Version

| Aspect | BST | Binary Tree |
|--------|-----|-------------|
| Navigation | Use value comparison | Must search both subtrees |
| Time | O(h) | O(n) |
| Approach | Top-down | Bottom-up |

## Related Problems

- [Lowest Common Ancestor of a BST](problems/19_lowest_common_ancestor_of_a_bst.md) - BST version (easier)
- [Subtree of Another Tree](problems/29_subtree_of_another_tree.md)