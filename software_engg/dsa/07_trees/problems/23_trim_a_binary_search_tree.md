# Trim a Binary Search Tree

## Question

Given the `root` of a binary search tree and two integers `low` and `high`, trim the tree so that all its elements lie within the range `[low, high]`.

Trimming the tree should **not** change the structure of the remaining elements. The relative structure of the remaining elements should be preserved.

Return the new root of the trimmed binary search tree.

## Examples

### Example 1
```
Input: root = [1,0,2], low = 1, high = 2
       1              1
      / \      =>     \
     0   2             2

Output: [1,null,2]
Explanation: Node 0 is less than low=1, so it's removed.
```

### Example 2
```
Input: root = [3,0,4,null,2,null,null,1], low = 1, high = 3
         3               3
        / \             / 
       0   4    =>     2   
        \              /    
         2            1      
        /                      
       1                       

Output: [3,2,null,1]
Explanation: Nodes 0, 4 are out of range and removed.
```

### Example 3
```
Input: root = [1], low = 1, high = 2
       1

Output: [1]
```

### Example 4
```
Input: root = [1,null,2], low = 1, high = 3
       1
        \
         2

Output: [1,null,2]
```

## Constraints

- The number of nodes in the tree is in the range `[1, 10^4]`.
- `0 <= Node.val <= 10^4`
- All node values are unique.
- `0 <= low <= high <= 10^4`

## Solution Approaches

### Approach 1: Recursive
```python
def trimBST(root, low, high):
    if not root:
        return None
    
    # If current node is less than low, trim left subtree
    # and return trimmed right subtree
    if root.val < low:
        return trimBST(root.right, low, high)
    
    # If current node is greater than high, trim right subtree
    # and return trimmed left subtree
    if root.val > high:
        return trimBST(root.left, low, high)
    
    # Current node is within range, trim both subtrees
    root.left = trimBST(root.left, low, high)
    root.right = trimBST(root.right, low, high)
    
    return root
```

### Approach 2: Iterative
```python
def trimBST(root, low, high):
    if not root:
        return None
    
    # Find the new root (first node within range)
    while root and (root.val < low or root.val > high):
        if root.val < low:
            root = root.right
        else:
            root = root.left
    
    if not root:
        return None
    
    # Trim left subtree
    current = root
    while current.left:
        if current.left.val < low:
            current.left = current.left.right
        else:
            current = current.left
    
    # Trim right subtree
    current = root
    while current.right:
        if current.right.val > high:
            current.right = current.right.left
        else:
            current = current.right
    
    return root
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(n) | O(h) - recursion stack |
| Iterative | O(n) | O(1) |

Where n = number of nodes, h = height of tree

## Key Insights

- **BST property**: If node < low, entire left subtree is < low (can be discarded)
- **BST property**: If node > high, entire right subtree is > high (can be discarded)
- **Preserve structure**: Only remove nodes outside range, keep relative structure

## Visual Explanation

```
Trim [1,3] from:
         3               3
        / \             / 
       0   4    =>     2   
        \              /    
         2            1      
        /                      
       1                      

Steps:
1. Root 3 is in range [1,3], keep it
2. Left subtree of 3: node 0 < 1, discard and use its right subtree (2)
3. Node 2 is in range, keep it
4. Left subtree of 2: node 1 is in range, keep it
5. Right subtree of 3: node 4 > 3, discard
```

## Algorithm Steps

1. If root is null, return null
2. If root.val < low:
   - Entire left subtree is invalid
   - Recursively trim right subtree
3. If root.val > high:
   - Entire right subtree is invalid
   - Recursively trim left subtree
4. If root.val is in range:
   - Recursively trim both subtrees
5. Return root

## Related Problems

- [Validate Binary Search Tree](problems/18_validate_binary_search_tree.md)
- [Insert into a Binary Search Tree](problems/21_insert_into_a_binary_search_tree.md)
- [Delete Node in a BST](problems/22_delete_node_in_a_bst.md)