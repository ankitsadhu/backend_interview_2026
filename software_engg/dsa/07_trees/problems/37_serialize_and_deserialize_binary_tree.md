# Serialize and Deserialize Binary Tree

## Question

Serialization is the process of converting a data structure or object into a sequence of bits so that it can be stored in a file or memory buffer, or transmitted across a network connection link to be reconstructed later in the same or another computer environment.

Design an algorithm to serialize and deserialize a binary tree. There is no restriction on how your serialization/deserialization algorithm should work. You just need to ensure that a binary tree can be serialized to a string and this string can be deserialized to the original tree structure.

## Examples

### Example 1
```
Input: root = [1,2,3,null,null,4,5]
       1
      / \
     2   3
        / \
       4   5

Output: [1,2,3,null,null,4,5]
```

### Example 2
```
Input: root = []
Output: []
```

### Example 3
```
Input: root = [1]
Output: [1]
```

### Example 4
```
Input: root = [1,2,3]
       1
      / \
     2   3

Output: [1,2,3]
```

## Constraints

- The number of nodes in the tree is in the range `[0, 10^4]`.
- `-1000 <= Node.val <= 1000`

## Solution Approaches

### Approach 1: Preorder Traversal (Recursive)
```python
class Codec:
    def serialize(self, root):
        """Encodes a tree to a single string."""
        result = []
        
        def preorder(node):
            if not node:
                result.append("null")
                return
            result.append(str(node.val))
            preorder(node.left)
            preorder(node.right)
        
        preorder(root)
        return ",".join(result)
    
    def deserialize(self, data):
        """Decodes your encoded data to tree."""
        if not data:
            return None
        
        values = iter(data.split(","))
        
        def build():
            val = next(values)
            if val == "null":
                return None
            node = TreeNode(int(val))
            node.left = build()
            node.right = build()
            return node
        
        return build()
```

### Approach 2: Level Order Traversal (BFS)
```python
class Codec:
    def serialize(self, root):
        """Encodes a tree to a single string."""
        if not root:
            return ""
        
        result = []
        queue = [root]
        
        while queue:
            node = queue.pop(0)
            if node:
                result.append(str(node.val))
                queue.append(node.left)
                queue.append(node.right)
            else:
                result.append("null")
        
        # Remove trailing nulls
        while result and result[-1] == "null":
            result.pop()
        
        return ",".join(result)
    
    def deserialize(self, data):
        """Decodes your encoded data to tree."""
        if not data:
            return None
        
        values = data.split(",")
        root = TreeNode(int(values[0]))
        queue = [root]
        i = 1
        
        while queue and i < len(values):
            node = queue.pop(0)
            
            if i < len(values) and values[i] != "null":
                node.left = TreeNode(int(values[i]))
                queue.append(node.left)
            i += 1
            
            if i < len(values) and values[i] != "null":
                node.right = TreeNode(int(values[i]))
                queue.append(node.right)
            i += 1
        
        return root
```

### Approach 3: Iterative Preorder (Stack)
```python
class Codec:
    def serialize(self, root):
        """Encodes a tree to a single string."""
        if not root:
            return ""
        
        result = []
        stack = [root]
        
        while stack:
            node = stack.pop()
            if node:
                result.append(str(node.val))
                stack.append(node.right)  # Push right first
                stack.append(node.left)
            else:
                result.append("null")
        
        return ",".join(result)
    
    def deserialize(self, data):
        """Decodes your encoded data to tree."""
        if not data:
            return None
        
        values = data.split(",")
        root = TreeNode(int(values[0]))
        stack = [(root, 0)]  # (node, state: 0=need left, 1=need right)
        i = 1
        
        while stack and i < len(values):
            node, state = stack[-1]
            
            if state == 0:
                stack[-1] = (node, 1)
                if values[i] != "null":
                    node.left = TreeNode(int(values[i]))
                    stack.append((node.left, 0))
                i += 1
            else:
                stack.pop()
                if values[i] != "null":
                    node.right = TreeNode(int(values[i]))
                    stack.append((node.right, 0))
                i += 1
        
        return root
```

## Complexity Analysis

| Approach | Serialize Time | Deserialize Time | Space |
|----------|----------------|------------------|-------|
| Preorder recursive | O(n) | O(n) | O(n) |
| Level order BFS | O(n) | O(n) | O(n) |
| Preorder iterative | O(n) | O(n) | O(n) |

Where n = number of nodes

## Key Insights

- **Null markers**: Use special value (like "null") to mark missing nodes
- **Preorder**: Root-Left-Right order allows reconstruction
- **Level order**: BFS order also works for reconstruction

## Visual Explanation

```
Tree:
       1
      / \
     2   3
        / \
       4   5

Preorder serialization:
Visit 1 -> "1"
Visit 2 -> "1,2"
Visit null (2's left) -> "1,2,null"
Visit null (2's right) -> "1,2,null,null"
Visit 3 -> "1,2,null,null,3"
Visit 4 -> "1,2,null,null,3,4"
Visit null -> "1,2,null,null,3,4,null"
Visit null -> "1,2,null,null,3,4,null,null"
Visit 5 -> "1,2,null,null,3,4,null,null,5"
Visit null -> "1,2,null,null,3,4,null,null,5,null"
Visit null -> "1,2,null,null,3,4,null,null,5,null,null"

Final: "1,2,null,null,3,4,null,null,5,null,null"
```

## Algorithm Steps (Preorder)

**Serialize:**
1. Perform preorder traversal
2. For each node, append its value
3. For null nodes, append "null"
4. Join with comma

**Deserialize:**
1. Split string by comma
2. Use iterator to get values
3. Recursively build tree in preorder

## Related Problems

- [Construct Binary Tree from Preorder and Inorder Traversal](problems/36_construct_binary_tree_from_preorder_and_inorder_traversal.md)
- [Binary Tree Level Order Traversal](problems/12_binary_tree_level_order_traversal.md)