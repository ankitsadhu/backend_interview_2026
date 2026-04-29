
# Populating Next Right Pointers in Each Node

## Question

You are given a **perfect binary tree** where all leaves are on the same level, and every parent has two children.

Populate each next pointer to point to its next right node. If there is no next right node, the next pointer should be set to `NULL`.

Initially, all next pointers are set to `NULL`.

The tree node structure is:
```python
class Node:
    def __init__(self, val: int = 0, left: 'Node' = None, right: 'Node' = None, next: 'Node' = None):
        self.val = val
        self.left = left
        self.right = right
        self.next = next
```

## Examples

### Example 1
```
Input: root = [1,2,3,4,5,6,7]
           1 -> NULL
         /   \
        2  -> 3 -> NULL
       / \   / \
      4->5->6->7 -> NULL

Output: [1,#,2,3,#,4,5,6,7,#]
Explanation: Each next pointer points to the next right node at the same level.
             '#' signifies the end of each level.
```

### Example 2
```
Input: root = []
Output: []
```

## Constraints

- The number of nodes in the tree is in the range `[0, 2^12 - 1]`.
- `-1000 <= Node.val <= 1000`
- The tree is a **perfect binary tree** (all leaves at same level, every parent has 2 children)

## Follow-up

- You may only use constant extra space.
- The recursive approach is fine for implicit stack space.

## Solution Approaches

### Approach 1: BFS (Level Order Traversal)
```python
from collections import deque

def connect(root):
    if not root:
        return None
    
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        
        for i in range(level_size):
            node = queue.popleft()
            
            # Set next pointer to next node in queue (or None if last)
            if i < level_size - 1:
                node.next = queue[0]
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    
    return root
```

### Approach 2: Using Already Established Next Pointers (O(1) Space)
```python
def connect(root):
    if not root:
        return None
    
    leftmost = root
    
    while leftmost.left:  # While there are more levels
        head = leftmost
        
        while head:
            # Connect left child to right child
            head.left.next = head.right
            
            # Connect right child to next node's left child
            if head.next:
                head.right.next = head.next.left
            
            head = head.next
        
        # Move to next level
        leftmost = leftmost.left
    
    return root
```

### Approach 3: Recursive DFS
```python
def connect(root):
    if not root or not root.left:
        return root
    
    # Connect left to right
    root.left.next = root.right
    
    # Connect right to next node's left
    if root.next:
        root.right.next = root.next.left
    
    # Recurse for children
    connect(root.left)
    connect(root.right)
    
    return root
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| BFS | O(n) | O(w) - queue width |
| Using next pointers | O(n) | O(1) - constant space |
| Recursive DFS | O(n) | O(h) - recursion stack |

Where n = number of nodes, h = height of tree, w = maximum width

## Key Insights

- **Perfect binary tree**: Every level is completely filled
- **Cross-parent connections**: Right child connects to left child of parent's next
- **O(1) space**: Can use already-established next pointers to traverse

## Visual Explanation

```
Before:                After:
       1                    1 -> NULL
     /   \                /   \
    2     3              2 ->  3 -> NULL
   / \   / \            / \   / \
  4   5 6   7          4->5->6->7 -> NULL

Key connections:
- 2.next = 3 (same parent)
- 5.next = 6 (different parents - use parent's next)
```

## Algorithm for O(1) Space

```
1. Start with leftmost = root
2. While leftmost has left child:
   a. Set head = leftmost
   b. While head exists:
      - head.left.next = head.right
      - if head.next exists: head.right.next = head.next.left
      - head = head.next
   c. leftmost = leftmost.left
```

## Related Problems

- [Populating Next Right Pointers in Each Node II](problems/17_populating_next_right_pointers_in_each_node_ii.md) - Not a perfect binary tree
- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md) - Level order traversal