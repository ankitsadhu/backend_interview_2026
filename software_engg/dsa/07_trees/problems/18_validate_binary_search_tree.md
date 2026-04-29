# Validate Binary Search Tree

## Question

Given the `root` of a binary tree, determine if it is a valid binary search tree (BST).

A **valid BST** is defined as follows:
- The left subtree of a node contains only nodes with keys **less than** the node's key.
- The right subtree of a node contains only nodes with keys **greater than** the node's key.
- Both the left and right subtrees must also be binary search trees.

## Examples

### Example 1
```
Input: root = [2,1,3]
       2
      / \
     1   3

Output: true
```

### Example 2
```
Input: root = [5,1,4,null,null,3,6]
       5
      / \
     1   4
        / \
       3   6

Output: false
Explanation: The root node's value is 5 but its right child's value is 4.
```

### Example 3
```
Input: root = [5,3,7,1,4,6,8]
          5
         / \
        3   7
       / \ / \
      1  4 6  8

Output: true
```

### Example 4
```
Input: root = [10,5,15,null,null,6,20]
          10
         /  \
        5    15
            /  \
           6    20

Output: false
Explanation: Node 6 is in the right subtree of 10 but is less than 10.
```

## Constraints

- The number of nodes in the tree is in the range `[1, 10^4]`.
- `-2^31 <= Node.val <= 2^31 - 1`

## Solution Approaches

### Approach 1: Recursive with Valid Range
```python
def isValidBST(root):
    def validate(node, low, high):
        if not node:
            return True
        
        # Current node must be within valid range
        if node.val <= low or node.val >= high:
            return False
        
        # Left subtree: values must be < node.val
        # Right subtree: values must be > node.val
        return (validate(node.left, low, node.val) and
                validate(node.right, node.val, high))
    
    return validate(root, float('-inf'), float('inf'))
```

### Approach 2: Inorder Traversal (Iterative)
```python
def isValidBST(root):
    stack = []
    prev = float('-inf')
    current = root
    
    while stack or current:
        # Go to leftmost node
        while current:
            stack.append(current)
            current = current.left
        
        current = stack.pop()
        
        # Check if inorder sequence is strictly increasing
        if current.val <= prev:
            return False
        prev = current.val
        
        current = current.right
    
    return True
```

### Approach 3: Inorder Traversal (Recursive)
```python
def isValidBST(root):
    prev = float('-inf')
    
    def inorder(node):
        nonlocal prev
        
        if not node:
            return True
        
        # Left subtree
        if not inorder(node.left):
            return False
        
        # Current node
        if node.val <= prev:
            return False
        prev = node.val
        
        # Right subtree
        return inorder(node.right)
    
    return inorder(root)
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive with range | O(n) | O(h) - recursion stack |
| Inorder iterative | O(n) | O(h) - explicit stack |
| Inorder recursive | O(n) | O(h) - recursion stack |

Where n = number of nodes, h = height of tree

## Key Insights

- **Range validation**: Each node has a valid range (min, max) it must satisfy
- **Inorder property**: Inorder traversal of BST gives sorted sequence
- **Strict inequality**: Values must be strictly less/greater (no duplicates)

## Common Mistakes

1. **Only checking immediate children**: Must ensure ALL nodes in left subtree < root
2. **Using <= instead of <**: BST requires strictly less/greater (no duplicates)
3. **Not handling null root**: Empty tree is a valid BST

## Visual Explanation

```
Valid BST:           Invalid BST:
       5                   5
      / \                 / \
     3   8               3   8
    / \ / \             / \ / \
   1  4 7  9           1  6 7  9

Inorder: 1,3,4,5,7,8,9  Inorder: 1,3,6,5,7,8,9
(sorted)                (NOT sorted - 6 > 5)
```

## Range Propagation

```
For node with value 5:
- Left subtree: values must be in range (-inf, 5)
- Right subtree: values must be in range (5, inf)

For left child (3) of 5:
- Its left subtree: (-inf, 3)
- Its right subtree: (3, 5)  <- Note upper bound is 5, not 3!
```

## Related Problems

- [Lowest Common Ancestor of a BST](problems/19_lowest_common_ancestor_of_a_bst.md)
- [Kth Smallest Element in a BST](problems/20_kth_smallest_element_in_a_bst.md)
- [Insert into a Binary Search Tree](problems/21_insert_into_a_binary_search_tree.md)