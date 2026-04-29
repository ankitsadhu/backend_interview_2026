# Kth Smallest Element in a BST

## Question

Given the `root` of a binary search tree, and an integer `k`, return the **kth smallest value** (1-indexed) of all the values of nodes in the tree.

## Examples

### Example 1
```
Input: root = [3,1,4,null,2], k = 1
       3
      / \
     1   4
      \
       2

Output: 1
Explanation: The smallest element is 1 (k=1)
```

### Example 2
```
Input: root = [5,3,6,2,4,null,null,1], k = 3
          5
         / \
        3   6
       / \
      2   4
     /
    1

Output: 3
Explanation: Inorder traversal: [1,2,3,4,5,6]
             The 3rd smallest element is 3
```

### Example 3
```
Input: root = [1], k = 1
       1

Output: 1
```

## Constraints

- The number of nodes in the tree is `n`.
- `1 <= k <= n <= 10^4`
- `0 <= Node.val <= 10^4`

## Follow-up

If the BST is modified often (insert/delete) and you need to find the kth smallest frequently, how would you optimize?

**Answer**: Augment the BST by storing the size of the left subtree at each node. This allows O(h) lookup.

## Solution Approaches

### Approach 1: Inorder Traversal (Iterative)
```python
def kthSmallest(root, k):
    stack = []
    current = root
    count = 0
    
    while stack or current:
        # Go to leftmost node
        while current:
            stack.append(current)
            current = current.left
        
        current = stack.pop()
        count += 1
        
        # Check if this is the kth element
        if count == k:
            return current.val
        
        current = current.right
    
    return -1  # Should never reach here
```

### Approach 2: Inorder Traversal (Recursive)
```python
def kthSmallest(root, k):
    result = []
    
    def inorder(node):
        if not node or len(result) >= k:
            return
        
        inorder(node.left)
        result.append(node.val)
        inorder(node.right)
    
    inorder(root)
    return result[k - 1]
```

### Approach 3: Recursive with Counter
```python
def kthSmallest(root, k):
    count = [0]  # Use list to allow modification in nested function
    
    def inorder(node):
        if not node:
            return None
        
        # Search left subtree
        left = inorder(node.left)
        if left is not None:
            return left
        
        # Process current node
        count[0] += 1
        if count[0] == k:
            return node.val
        
        # Search right subtree
        return inorder(node.right)
    
    return inorder(root)
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Iterative inorder | O(H + k) | O(H) - stack |
| Recursive inorder | O(n) | O(h) - recursion |
| Recursive with counter | O(H + k) | O(h) - recursion |

Where n = number of nodes, h = height of tree

## Key Insights

- **Inorder traversal of BST gives sorted sequence**
- **Early termination**: Stop once we find the kth element
- **Iterative is more efficient**: Can terminate early without visiting all nodes

## Visual Explanation

```
BST:                    Inorder traversal (sorted):
          5             1 -> 2 -> 3 -> 4 -> 5 -> 6
         / \            k=1: 1
        3   6           k=2: 2
       / \              k=3: 3  <- Answer
      2   4             k=4: 4
     /                  k=5: 5
    1                   k=6: 6
```

## Follow-up Solution: Augmented BST

```python
class AugmentedNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.left_size = 0  # Number of nodes in left subtree

class AugmentedBST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        # Insert and update left_size
        pass
    
    def kthSmallest(self, k):
        node = self.root
        while node:
            if k == node.left_size + 1:
                return node.val
            elif k <= node.left_size:
                node = node.left
            else:
                k -= (node.left_size + 1)
                node = node.right
        return -1
```

## Related Problems

- [Validate Binary Search Tree](problems/18_validate_binary_search_tree.md)
- [Lowest Common Ancestor of a BST](problems/19_lowest_common_ancestor_of_a_bst.md)
- [Binary Search Tree Iterator](problems/25_binary_search_tree_iterator.md)