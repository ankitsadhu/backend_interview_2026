# Subtree of Another Tree

## Question

Given the roots of two binary trees `root` and `subRoot`, return `true` if there is a subtree of `root` with the same structure and node values of `subRoot`, and `false` otherwise.

A **subtree** of a binary tree `tree` is a tree consisting of a node in `tree` and all of this node's descendants. The tree `tree` could also be considered as a subtree of itself.

## Examples

### Example 1
```
Input: root = [3,4,5,1,2], subRoot = [4,5,1,2]
          3                4
         / \              / \
        4   5    and     5   1
       / \
      1   2

Output: true
Explanation: The subtree rooted at node 4 in root matches subRoot exactly.
```

### Example 2
```
Input: root = [3,4,5,1,2,null,null,null,null,0], subRoot = [4,5,1,2]
             3                 4
            / \               / \
           4   5     and    5   1
          / \
         1   2
            /
           0

Output: false
Explanation: The subtree rooted at node 4 in root does not match subRoot.
```

### Example 3
```
Input: root = [1,1], subRoot = [1]
       1
      /
     1

Output: true
```

## Constraints

- The number of nodes in `root` is in the range `[1, 2000]`.
- The number of nodes in `subRoot` is in the range `[1, 1000]`.
- `-10^4 <= root.val <= 10^4`
- `-10^4 <= subRoot.val <= 10^4`

## Solution Approaches

### Approach 1: Recursive Comparison
```python
def isSubtree(root, subRoot):
    def isSameTree(p, q):
        if not p and not q:
            return True
        if not p or not q:
            return False
        return (p.val == q.val and 
                isSameTree(p.left, q.left) and 
                isSameTree(p.right, q.right))
    
    if not root:
        return False
    
    # Check if current tree matches subRoot
    if isSameTree(root, subRoot):
        return True
    
    # Check left and right subtrees
    return isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)
```

### Approach 2: String Serialization
```python
def isSubtree(root, subRoot):
    def serialize(node):
        if not node:
            return "#"
        return f"!{node.val}{serialize(node.left)}{serialize(node.right)}"
    
    tree_str = serialize(root)
    sub_str = serialize(subRoot)
    
    return sub_str in tree_str
```

### Approach 3: DFS with Hashing (Rabin-Karp)
```python
def isSubtree(root, subRoot):
    MOD = 10**9 + 7
    
    def hash_tree(node):
        if not node:
            return 3
        
        left_hash = hash_tree(node.left)
        right_hash = hash_tree(node.right)
        
        # Combine hashes
        return (left_hash * 257 + node.val * 31 + right_hash) % MOD
    
    sub_hash = hash_tree(subRoot)
    
    def dfs(node):
        if not node:
            return False
        
        if hash_tree(node) == sub_hash:
            if isSameTree(node, subRoot):
                return True
        
        return dfs(node.left) or dfs(node.right)
    
    def isSameTree(p, q):
        if not p and not q:
            return True
        if not p or not q:
            return False
        return (p.val == q.val and 
                isSameTree(p.left, q.left) and 
                isSameTree(p.right, q.right))
    
    return dfs(root)
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive | O(m * n) | O(max(m, n)) - recursion |
| String serialization | O(m + n) | O(m + n) - strings |
| Hashing | O(m + n) average | O(max(m, n)) - recursion |

Where m = nodes in root, n = nodes in subRoot

## Key Insights

- **Two-step process**: Find potential root match, then verify entire subtree
- **String matching**: Serialization converts tree problem to string problem
- **Early termination**: Return true as soon as match is found

## Visual Explanation

```
root:                    subRoot:
          3                    4
         / \                  / \
        4   5                5   1
       / \
      1   2

Step 1: Start at root (3), compare with subRoot (4) - no match
Step 2: Go to left child (4), compare with subRoot (4) - match!
Step 3: Verify entire subtree matches - yes!
Return true
```

## Algorithm Steps

1. If root is null, return false (empty tree has no subtrees)
2. Check if tree rooted at current node matches subRoot
3. If yes, return true
4. Otherwise, recursively check left and right subtrees
5. Return true if any subtree matches

## Related Problems

- [Same Tree](problems/06_same_tree.md) - Check if two trees are identical
- [Lowest Common Ancestor of a Binary Tree](problems/30_lowest_common_ancestor_of_binary_tree.md)