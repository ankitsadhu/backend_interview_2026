# Convert BST to Greater Tree

## Question

Given the `root` of a Binary Search Tree, convert it to a **Greater Tree** such that every key of the original BST is changed to the original key plus the sum of all keys **greater than** the original key in BST.

A Binary Search Tree satisfies the following constraints:
- The left subtree of a node contains only nodes with keys **less than** the node's key.
- The right subtree of a node contains only nodes with keys **greater than** the node's key.
- Both subtrees must also be binary search trees.

## Examples

### Example 1
```
Input: root = [4,1,6,0,2,5,7,null,null,null,3,null,null,null,8]
              4                         30
            /   \                      /   \
           1     6                   36     21
          / \   / \       =>         / \    / \
         0  2  5   7               36  35 26  8
            / \      \                  / \      \
           3   4      8                33  30     8

Output: [30,36,21,36,35,26,8,null,null,null,33,null,null,null,8]
```

### Example 2
```
Input: root = [0,null,1]
       0              1
        \      =>     \
         1             1

Output: [1,null,1]
```

### Example 3
```
Input: root = [1,0,2]
       1              3
      / \      =>    / \
     0   2          3   2

Output: [3,3,2]
```

### Example 4
```
Input: root = [3,2,4,1]
       3              7
      / \            / \
     2   4    =>    9   4
    /              /
   1              10

Output: [7,9,4,10]
```

## Constraints

- The number of nodes in the tree is in the range `[1, 100]`.
- `0 <= Node.val <= 100`
- All the values in the tree are unique.

## Solution Approaches

### Approach 1: Reverse Inorder Traversal (Recursive)
```python
def convertBST(root):
    total = [0]  # Use list to allow modification
    
    def reverse_inorder(node):
        if not node:
            return
        
        # Traverse right subtree first (greater values)
        reverse_inorder(node.right)
        
        # Update current node
        total[0] += node.val
        node.val = total[0]
        
        # Traverse left subtree (smaller values)
        reverse_inorder(node.left)
    
    reverse_inorder(root)
    return root
```

### Approach 2: Reverse Inorder Traversal (Iterative)
```python
def convertBST(root):
    total = 0
    stack = []
    current = root
    
    while stack or current:
        # Go to rightmost node
        while current:
            stack.append(current)
            current = current.right
        
        current = stack.pop()
        
        # Update current node
        total += current.val
        current.val = total
        
        # Go to left subtree
        current = current.left
    
    return root
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(n) | O(h) - recursion stack |
| Iterative | O(n) | O(h) - explicit stack |

Where n = number of nodes, h = height of tree

## Key Insights

- **Reverse inorder**: Right → Root → Left gives descending order
- **Running sum**: Keep track of sum of all visited nodes
- **In-place modification**: Update node values as we traverse

## Visual Explanation

```
Original BST (inorder: 0,1,2,3,4,5,6,7,8):
              4
            /   \
           1     6
          / \   / \
         0  2  5   7
            / \      \
           3   4      8

Reverse inorder traversal with running sum:
Visit 8: sum=8,  node.val=8
Visit 7: sum=15, node.val=15
Visit 6: sum=21, node.val=21
Visit 5: sum=26, node.val=26
Visit 4: sum=30, node.val=30
Visit 3: sum=33, node.val=33
Visit 2: sum=35, node.val=35
Visit 1: sum=36, node.val=36
Visit 0: sum=36, node.val=36

Greater Tree:
              30
            /   \
           36    21
          / \   / \
         36 35 26  8
            / \      \
           33 30      8
```

## Algorithm Steps

1. Initialize `total = 0`
2. Perform reverse inorder traversal (right → root → left)
3. For each node:
   - Add node's value to `total`
   - Update node's value to `total`
4. Return modified root

## Why Reverse Inorder?

- In a BST, inorder gives ascending order
- Reverse inorder gives **descending order**
- Processing in descending order ensures we've seen all greater values before current node

## Related Problems

- [Binary Search Tree Iterator](problems/25_binary_search_tree_iterator.md)
- [Validate Binary Search Tree](problems/18_validate_binary_search_tree.md)
- [Convert Sorted Array to BST](problems/24_convert_sorted_array_to_bst.md)