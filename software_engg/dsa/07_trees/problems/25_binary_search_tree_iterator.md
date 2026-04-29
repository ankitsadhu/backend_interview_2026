# Binary Search Tree Iterator

## Question

Implement the `BSTIterator` class that represents an iterator over the **inorder traversal** of a binary search tree (BST):

- `BSTIterator(TreeNode root)` - Initializes an object of the BSTIterator class. The root of the BST is given as part of the constructor. The pointer should be initialized to a non-existent number smaller than any element in the BST.
- `boolean hasNext()` - Returns true if there exists a number in the traversal to the right of the pointer, otherwise returns false.
- `int next()` - Moves the pointer to the right, then returns the number at the pointer.

Notice that by initializing the pointer to a non-existent smallest number, the first call to `next()` will return the smallest element in the BST.

You may assume that `next()` calls will always be valid. That is, there will be at least a next number in the in-order traversal when `next()` is called.

## Examples

### Example
```
Input
["BSTIterator", "next", "next", "hasNext", "next", "hasNext", "next", "hasNext", "next", "hasNext"]
[[[7, 3, 15, null, null, 9, 20]], [], [], [], [], [], [], [], [], []]

Output
[null, 3, 7, true, 9, true, 15, true, 20, false]

Explanation
BSTIterator bSTIterator = new BSTIterator([7, 3, 15, null, null, 9, 20]);
          7
         / \
        3   15
           /  \
          9   20

bSTIterator.next();    // return 3
bSTIterator.next();    // return 7
bSTIterator.hasNext(); // return True
bSTIterator.next();    // return 9
bSTIterator.hasNext(); // return True
bSTIterator.next();    // return 15
bSTIterator.hasNext(); // return True
bSTIterator.next();    // return 20
bSTIterator.hasNext(); // return False
```

## Constraints

- The number of nodes in the tree is in the range `[1, 10^5]`.
- `0 <= Node.val <= 10^6`
- At most `10^5` calls will be made to `hasNext`, and `next`.

## Follow-up

Could you implement `next()` and `hasNext()` to run in average **O(1)** time and use **O(h)** memory, where `h` is the height of the tree?

## Solution Approaches

### Approach 1: Controlled Inorder Traversal (O(1) average, O(h) memory)
```python
class BSTIterator:
    def __init__(self, root):
        self.stack = []
        self._pushLeft(root)
    
    def _pushLeft(self, node):
        """Push all left nodes onto stack"""
        while node:
            self.stack.append(node)
            node = node.left
    
    def next(self):
        """Returns the next smallest number"""
        node = self.stack.pop()
        # If node has right subtree, push its left branch
        if node.right:
            self._pushLeft(node.right)
        return node.val
    
    def hasNext(self):
        """Returns whether there is a next number"""
        return len(self.stack) > 0
```

### Approach 2: Precompute Inorder Traversal (O(1) time, O(n) memory)
```python
class BSTIterator:
    def __init__(self, root):
        self.inorder = []
        self.index = 0
        
        # Compute full inorder traversal
        stack = []
        current = root
        while stack or current:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            self.inorder.append(current.val)
            current = current.right
    
    def next(self):
        val = self.inorder[self.index]
        self.index += 1
        return val
    
    def hasNext(self):
        return self.index < len(self.inorder)
```

### Approach 3: Recursive Inorder (O(1) average, O(h) memory)
```python
class BSTIterator:
    def __init__(self, root):
        self.stack = []
        self._inorder_left(root)
    
    def _inorder_left(self, node):
        while node:
            self.stack.append(node)
            node = node.left
    
    def next(self):
        topmost = self.stack.pop()
        if topmost.right:
            self._inorder_left(topmost.right)
        return topmost.val
    
    def hasNext(self):
        return len(self.stack) > 0
```

## Complexity Analysis

| Approach | next() Time | hasNext() Time | Space |
|----------|-------------|----------------|-------|
| Controlled traversal | Amortized O(1) | O(1) | O(h) |
| Precompute | O(1) | O(1) | O(n) |
| Recursive | Amortized O(1) | O(1) | O(h) |

Where h = height of tree

## Key Insights

- **Lazy evaluation**: Only process nodes as needed
- **Stack simulates recursion**: Mimics the call stack of recursive inorder traversal
- **Amortized O(1)**: Each node is pushed and popped exactly once

## Visual Explanation

```
Tree:
          7
         / \
        3   15
           /  \
          9   20

Stack state during iteration:

Initial: [7, 3]  (pushed all left from root)
next() -> 3, stack: [7]
next() -> 7, stack: [15] (pushed right subtree's left)
next() -> 9, stack: [15]
next() -> 15, stack: [20]
next() -> 20, stack: []
```

## Algorithm Steps

1. **Initialization**: Push all left nodes from root onto stack
2. **next()**: 
   - Pop top node from stack
   - If it has a right child, push all left nodes of right subtree
   - Return the popped node's value
3. **hasNext()**: Check if stack is non-empty

## Why Amortized O(1)?

- Each node is pushed onto stack exactly once
- Each node is popped from stack exactly once
- Total operations for n nodes: O(n)
- Average per call: O(n) / n = O(1)

## Related Problems

- [Kth Smallest Element in a BST](problems/20_kth_smallest_element_in_a_bst.md)
- [Inorder Successor in BST](problems/)
- [Flatten Binary Tree to Linked List](problems/38_flatten_binary_tree_to_linked_list.md)