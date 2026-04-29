# Delete Node in a BST

## Question

Given the `root` of a binary search tree (BST) and a `key`, delete the node with the given `key` in the BST. Return the (possibly empty) root node reference of the updated BST.

The deletion process involves two stages:
1. Search for the node to remove.
2. If the node is found, delete the node.

## Examples

### Example 1
```
Input: root = [5,3,6,2,4,null,7], key = 3
        5                 5
       / \               / \
      3   6    =>       4   6
     / \   \           / \   \
    2   4   7         2   4   7

Output: [5,4,6,2,null,null,7]
Explanation: Node with value 3 is deleted. One valid result is shown.
```

### Example 2
```
Input: root = [5,3,6,2,4,null,7], key = 0
        5                 5
       / \               / \
      3   6    =>       3   6
     / \   \           / \   \
    2   4   7         2   4   7

Output: [5,3,6,2,4,null,7]
Explanation: Node with value 0 does not exist, tree unchanged.
```

### Example 3
```
Input: root = [], key = 0
Output: []
```

### Example 4
```
Input: root = [5,3,6,2,4,null,7], key = 5
        5                 6
       / \               / \
      3   6    =>       3   7
     / \   \           / \
    2   4   7         2   4

Output: [6,3,7,2,4]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 10^4]`.
- `-10^5 <= Node.val <= 10^5`
- All node values are unique.
- `key` is a valid node value in the BST or doesn't exist.

## Solution Approaches

### Approach: Recursive
```python
def deleteNode(root, key):
    if not root:
        return None
    
    # Search for the node
    if key < root.val:
        root.left = deleteNode(root.left, key)
    elif key > root.val:
        root.right = deleteNode(root.right, key)
    else:
        # Node found - three cases
        
        # Case 1: Node has no children (leaf)
        if not root.left and not root.right:
            return None
        
        # Case 2: Node has only one child
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        
        # Case 3: Node has two children
        # Find the inorder successor (smallest in right subtree)
        successor = findMin(root.right)
        root.val = successor.val
        # Delete the successor
        root.right = deleteNode(root.right, successor.val)
    
    return root

def findMin(node):
    while node.left:
        node = node.left
    return node
```

### Approach: Iterative
```python
def deleteNode(root, key):
    if not root:
        return None
    
    # Find the node and its parent
    current = root
    parent = None
    
    while current and current.val != key:
        parent = current
        if key < current.val:
            current = current.left
        else:
            current = current.right
    
    # Node not found
    if not current:
        return root
    
    # Node has two children
    if current.left and current.right:
        # Find inorder successor
        successor = current.right
        successor_parent = current
        while successor.left:
            successor_parent = successor
            successor = successor.left
        
        # Copy successor's value
        current.val = successor.val
        
        # Delete successor (it has at most one child)
        if successor_parent.left == successor:
            successor_parent.left = successor.right
        else:
            successor_parent.right = successor.right
        
        return root
    
    # Node has zero or one child
    child = current.left if current.left else current.right
    
    if not parent:  # Deleting root
        return child
    
    if parent.left == current:
        parent.left = child
    else:
        parent.right = child
    
    return root
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(h) | O(h) - recursion stack |
| Iterative | O(h) | O(1) |

Where h = height of tree (O(log n) for balanced BST, O(n) for skewed)

## Key Insights

- **Three deletion cases**:
  1. **Leaf node**: Simply remove it
  2. **One child**: Replace with child
  3. **Two children**: Replace with inorder successor (or predecessor)
- **Inorder successor**: Smallest node in right subtree (leftmost node)
- **BST property maintained**: After deletion, tree remains a valid BST

## Visual Explanation

```
Delete node 3 (has two children):
        5                 5
       / \               / \
      3   6    =>       4   6
     / \   \           / \   \
    2   4   7         2   4   7

Steps:
1. Find node 3
2. Find inorder successor: 4 (smallest in right subtree)
3. Replace 3 with 4
4. Delete original 4 (it's a leaf or has one child)
```

## Algorithm Steps

1. Search for the node with the given key
2. If not found, return the original tree
3. If found, handle three cases:
   - **No children**: Return None
   - **One child**: Return the child
   - **Two children**: 
     a. Find inorder successor (min of right subtree)
     b. Copy successor's value to current node
     c. Recursively delete the successor

## Related Problems

- [Insert into a Binary Search Tree](problems/21_insert_into_a_binary_search_tree.md)
- [Validate Binary Search Tree](problems/18_validate_binary_search_tree.md)
- [Lowest Common Ancestor of a BST](problems/19_lowest_common_ancestor_of_a_bst.md)