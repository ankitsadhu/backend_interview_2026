# Construct Binary Tree from Preorder and Inorder Traversal

## Question

Given two integer arrays `preorder` and `inorder` where `preorder` is the preorder traversal of a binary tree and `inorder` is the inorder traversal of the same tree, construct and return the binary tree.

## Examples

### Example 1
```
Input: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
Output: [3,9,20,null,null,15,7]

Tree structure:
       3
      / \
     9  20
       /  \
      15   7
```

### Example 2
```
Input: preorder = [-1], inorder = [-1]
Output: [-1]
```

### Example 3
```
Input: preorder = [1,2,4,5,3,6,7], inorder = [4,2,5,1,6,3,7]
Output: [1,2,3,4,5,6,7]

Tree structure:
          1
         / \
        2   3
       / \ / \
      4  5 6  7
```

## Constraints

- `1 <= preorder.length <= 3000`
- `inorder.length == preorder.length`
- `-3000 <= preorder[i], inorder[i] <= 3000`
- `preorder` and `inorder` consist of unique values.
- Each value of `inorder` also appears in `preorder`.
- `preorder` is guaranteed to be the preorder traversal of a binary tree.
- `inorder` is guaranteed to be the inorder traversal of the same binary tree.

## Solution Approaches

### Approach 1: Recursive with Hash Map
```python
def buildTree(preorder, inorder):
    if not preorder or not inorder:
        return None
    
    # Create hash map for O(1) lookup
    inorder_map = {val: i for i, val in enumerate(inorder)}
    
    def build(pre_left, pre_right, in_left, in_right):
        if pre_left > pre_right or in_left > in_right:
            return None
        
        # Root is the first element in preorder
        root_val = preorder[pre_left]
        root = TreeNode(root_val)
        
        # Find root position in inorder
        in_root = inorder_map[root_val]
        
        # Calculate size of left subtree
        left_size = in_root - in_left
        
        # Build left subtree
        root.left = build(pre_left + 1, pre_left + left_size, in_left, in_root - 1)
        
        # Build right subtree
        root.right = build(pre_left + left_size + 1, pre_right, in_root + 1, in_right)
        
        return root
    
    return build(0, len(preorder) - 1, 0, len(inorder) - 1)
```

### Approach 2: Recursive with Iterator
```python
def buildTree(preorder, inorder):
    if not preorder or not inorder:
        return None
    
    inorder_map = {val: i for i, val in enumerate(inorder)}
    preorder_iter = iter(preorder)
    
    def build(in_left, in_right):
        if in_left > in_right:
            return None
        
        # Get next value from preorder
        root_val = next(preorder_iter)
        root = TreeNode(root_val)
        
        # Find position in inorder
        in_root = inorder_map[root_val]
        
        # Build left then right (important order!)
        root.left = build(in_left, in_root - 1)
        root.right = build(in_root + 1, in_right)
        
        return root
    
    return build(0, len(inorder) - 1)
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive with map | O(n) | O(n) - map + recursion |
| Recursive with iterator | O(n) | O(n) - map + recursion |

Where n = number of nodes

## Key Insights

- **Preorder**: Root → Left → Right (first element is always root)
- **Inorder**: Left → Root → Right (elements left of root are in left subtree)
- **Hash map**: Use map to quickly find root position in inorder

## Visual Explanation

```
preorder = [3,9,20,15,7]
inorder = [9,3,15,20,7]

Step 1: Root = 3 (first in preorder)
        In inorder: [9] 3 [15,20,7]
        Left subtree: [9], Right subtree: [15,20,7]

Step 2: Left subtree
        preorder: [9], inorder: [9]
        Root = 9, no children

Step 3: Right subtree
        preorder: [20,15,7], inorder: [15,20,7]
        Root = 20
        In inorder: [15] 20 [7]
        Left: [15], Right: [7]

Final tree:
       3
      / \
     9  20
       /  \
      15   7
```

## Algorithm Steps

1. First element of preorder is the root
2. Find root in inorder - elements to left are left subtree, right are right subtree
3. Recursively build left subtree
4. Recursively build right subtree
5. Return root

## Related Problems

- [Construct Binary Tree from Inorder and Postorder Traversal](problems/)
- [Serialize and Deserialize Binary Tree](problems/37_serialize_and_deserialize_binary_tree.md)
- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md)