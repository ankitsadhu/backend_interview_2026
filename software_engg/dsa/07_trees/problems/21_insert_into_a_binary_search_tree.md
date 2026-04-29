# Insert into a Binary Search Tree

## Question

You are given the `root` of a binary search tree (BST) and a `val` to insert into the tree. Return the root node of the BST after the insertion.

It is **guaranteed** that the new value does not exist in the original BST.

**Note**: There may exist multiple valid ways to insert the value, as long as the tree remains a BST. Return any valid result.

## Examples

### Example 1
```
Input: root = [4,2,7,1,3], val = 5
       4                4
      / \              / \
     2   7    =>      2   7
    / \              / \  /
   1   3            1  3 5

Output: [4,2,7,1,3,5]
```

### Example 2
```
Input: root = [40,20,60,10,30,50,70], val = 25
        40                 40
       /  \               /  \
      20   60    =>      20   60
     / \   / \          / \   / \
    10 30 50 70        10 30 50 70
              \                 \
               25                25

Output: [40,20,60,10,30,50,70,null,null,25]
```

### Example 3
```
Input: root = [4,2,7,1,3,null,null,null,null,null,null], val = 5
       4                4
      / \              / \
     2   7    =>      2   7
    / \              / \  /
   1   3            1  3 5

Output: [4,2,7,1,3,5]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 10^4]`.
- `-10^8 <= Node.val <= 10^8`
- All the values `Node.val` are unique.
- `-10^8 <= val <= 10^8`
- It's guaranteed that `val` does not exist in the original BST.

## Solution Approaches

### Approach 1: Recursive
```python
def insertIntoBST(root, val):
    # Base case: found insertion point
    if not root:
        return TreeNode(val)
    
    # Insert into appropriate subtree
    if val < root.val:
        root.left = insertIntoBST(root.left, val)
    else:
        root.right = insertIntoBST(root.right, val)
    
    return root
```

### Approach 2: Iterative
```python
def insertIntoBST(root, val):
    # Handle empty tree
    if not root:
        return TreeNode(val)
    
    current = root
    while current:
        if val < current.val:
            if not current.left:
                current.left = TreeNode(val)
                break
            current = current.left
        else:
            if not current.right:
                current.right = TreeNode(val)
                break
            current = current.right
    
    return root
```

### Approach 3: Iterative with Parent Tracking
```python
def insertIntoBST(root, val):
    if not root:
        return TreeNode(val)
    
    current = root
    parent = None
    
    # Find the insertion point
    while current:
        parent = current
        if val < current.val:
            current = current.left
        else:
            current = current.right
    
    # Insert as child of parent
    if val < parent.val:
        parent.left = TreeNode(val)
    else:
        parent.right = TreeNode(val)
    
    return root
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(h) | O(h) - recursion stack |
| Iterative | O(h) | O(1) |
| Iterative with parent | O(h) | O(1) |

Where h = height of tree (O(log n) for balanced BST, O(n) for skewed)

## Key Insights

- **BST property**: Left < Root < Right
- **Always insert as leaf**: New node is always added as a leaf
- **Unique values**: No need to handle duplicate values

## Visual Explanation

```
Insert 5 into:
       4                4
      / \              / \
     2   7    =>      2   7
    / \              / \  /
   1   3            1  3 5

Steps:
1. Start at 4: 5 > 4, go right
2. At 7: 5 < 7, go left
3. 7 has no left child: insert 5 as left child of 7
```

## Algorithm Steps

1. If tree is empty, create new node as root
2. Start from root
3. Compare val with current node:
   - If val < current.val: go left
   - If val > current.val: go right
4. When we find a null child, insert new node there
5. Return root

## Related Problems

- [Delete Node in a BST](problems/22_delete_node_in_a_bst.md)
- [Validate Binary Search Tree](problems/18_validate_binary_search_tree.md)
- [Search in a Binary Search Tree](problems/) - Find a value in BST