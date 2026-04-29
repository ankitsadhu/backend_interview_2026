# Populating Next Right Pointers in Each Node II

## Question

Given a binary tree, populate each next pointer to point to its next right node. If there is no next right node, the next pointer should be set to `NULL`.

Initially, all next pointers are set to `NULL`.

Unlike the previous version, this tree is **not necessarily a perfect binary tree**.

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
Input: root = [1,2,3,4,5,null,7]
           1 -> NULL
         /   \
        2  -> 3 -> NULL
       / \     \
      4-> 5 -> 7 -> NULL

Output: [1,#,2,3,#,4,5,7,#]
Explanation: Each next pointer points to the next right node at the same level.
             '#' signifies the end of each level.
```

### Example 2
```
Input: root = []
Output: []
```

### Example 3
```
Input: root = [1,2]
       1
      /
     2

Output: [1,#,2,#]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 6000]`.
- `-100 <= Node.val <= 100`

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

### Approach 2: Using Next Pointers (O(1) Space)
```python
def connect(root):
    if not root:
        return None
    
    current = root
    
    while current:
        # Create a dummy node for the next level
        dummy = Node(0)
        tail = dummy
        
        # Process all nodes at current level
        node = current
        while node:
            if node.left:
                tail.next = node.left
                tail = tail.next
            if node.right:
                tail.next = node.right
                tail = tail.next
            node = node.next
        
        # Move to next level
        current = dummy.next
    
    return root
```

### Approach 3: Recursive DFS
```python
def connect(root):
    def get_next(node):
        """Find the next available child of node's next pointers"""
        if not node.next:
            return None
        if node.next.left:
            return node.next.left
        if node.next.right:
            return node.next.right
        return get_next(node.next)
    
    def dfs(node):
        if not node:
            return
        
        # Connect right child first (so next pointers are set)
        if node.right:
            if node.left:
                node.right.next = get_next(node)
            else:
                node.right.next = get_next(node)
        
        # Connect left child
        if node.left:
            if node.right:
                node.left.next = node.right
            else:
                node.left.next = get_next(node)
        
        # Recurse - right first to establish next pointers
        dfs(node.right)
        dfs(node.left)
    
    dfs(root)
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

- **Not perfect tree**: Some nodes may have only one child or be missing
- **Dummy node technique**: Use a dummy node to build the next level's connections
- **Process right first**: In DFS, process right subtree first to establish next pointers

## Difference from Problem I

| Aspect | Problem I (Perfect) | Problem II (Any) |
|--------|---------------------|------------------|
| Tree type | Perfect binary tree | Any binary tree |
| Every parent | Has 2 children | May have 0, 1, or 2 |
| O(1) approach | Simple cross-connection | Dummy node technique |
| DFS order | Any order works | Must process right first |

## Visual Explanation

```
Input: [1,2,3,4,5,null,7]

       1 -> NULL
     /   \
    2  -> 3 -> NULL
   / \     \
  4-> 5 -> 7 -> NULL

Note: Node 3 has no left child, only right child (7)
      Node 5 connects to 7 (not to null)
```

## Algorithm for O(1) Space

```
1. Start with current = root
2. While current exists:
   a. Create dummy node for next level
   b. Set tail = dummy
   c. For each node at current level:
      - If node.left exists: tail.next = node.left, tail = tail.next
      - If node.right exists: tail.next = node.right, tail = tail.next
   d. current = dummy.next (move to next level)
```

## Related Problems

- [Populating Next Right Pointers in Each Node](problems/16_populating_next_right_pointers_in_each_node.md) - Perfect binary tree
- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md) - Level order traversal