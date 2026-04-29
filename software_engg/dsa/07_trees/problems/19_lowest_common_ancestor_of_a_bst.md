# Lowest Common Ancestor of a BST

## Question

Given a binary search tree (BST), find the **lowest common ancestor** (LCA) of two given nodes in the BST.

The lowest common ancestor is defined between two nodes `p` and `q` as the lowest node in the tree that has both `p` and `q` as descendants (where we allow a node to be a descendant of itself).

## Examples

### Example 1
```
Input: root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 8
              6
            /   \
           2     8
          / \   / \
         0   4 7   9
            / \
           3   5

Output: 6
Explanation: The LCA of nodes 2 and 8 is 6.
```

### Example 2
```
Input: root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 4
              6
            /   \
           2     8
          / \   / \
         0   4 7   9
            / \
           3   5

Output: 2
Explanation: The LCA of nodes 2 and 4 is 2, since a node can be a descendant of itself.
```

### Example 3
```
Input: root = [2,1], p = 2, q = 1
       2
      /
     1

Output: 2
```

## Constraints

- The number of nodes in the tree is in the range `[2, 10^5]`.
- `-10^9 <= Node.val <= 10^9`
- All `Node.val` are unique.
- `p != q`
- `p` and `q` will exist in the BST.

## Solution Approaches

### Approach 1: Iterative (Using BST Property)
```python
def lowestCommonAncestor(root, p, q):
    current = root
    
    while current:
        # Both p and q are in right subtree
        if p.val > current.val and q.val > current.val:
            current = current.right
        # Both p and q are in left subtree
        elif p.val < current.val and q.val < current.val:
            current = current.left
        # Split point found - current is LCA
        else:
            return current
    
    return None
```

### Approach 2: Recursive (Using BST Property)
```python
def lowestCommonAncestor(root, p, q):
    if not root:
        return None
    
    # Both in right subtree
    if p.val > root.val and q.val > root.val:
        return lowestCommonAncestor(root.right, p, q)
    
    # Both in left subtree
    if p.val < root.val and q.val < root.val:
        return lowestCommonAncestor(root.left, p, q)
    
    # Split point - current node is LCA
    return root
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Iterative | O(h) | O(1) |
| Recursive | O(h) | O(h) - recursion stack |

Where h = height of tree (O(log n) for balanced BST, O(n) for skewed)

## Key Insights

- **BST property**: Left < Root < Right
- **Split point**: LCA is where p and q diverge to different subtrees
- **No need to search entire tree**: Use BST property to navigate

## Visual Explanation

```
Find LCA of 2 and 8:
              6              Start at 6
            /   \            2 < 6, 8 > 6 -> split point!
           2     8          
          / \   / \         
         0   4 7   9        

Find LCA of 2 and 4:
              6              Start at 6
            /   \            2 < 6, 4 < 6 -> go left
           2     8          At 2: 2 == 2, 4 > 2 -> split point!
          / \   / \         
         0   4 7   9        
```

## Related Problems

- [Lowest Common Ancestor of Binary Tree](problems/30_lowest_common_ancestor_of_binary_tree.md) - General binary tree (not BST)
- [Validate Binary Search Tree](problems/18_validate_binary_search_tree.md)