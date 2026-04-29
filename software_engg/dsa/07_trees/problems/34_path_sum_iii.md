# Path Sum III

## Question

Given the `root` of a binary tree and an integer `targetSum`, return the number of paths where the sum of the values along the path equals `targetSum`.

The path does **not** need to start or end at the root or a leaf, but it must go **downwards** (traveling only from parent nodes to child nodes).

## Examples

### Example 1
```
Input: root = [10,5,-3,3,2,null,11,3,-2,null,1], targetSum = 8
          10
         /  \
        5   -3
       / \    \
      3   2   11
     / \   \
    3  -2  1

Output: 3
Explanation: The paths that sum to 8 are:
1. 5 -> 3
2. 5 -> 2 -> 1
3. -3 -> 11
```

### Example 2
```
Input: root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
              5
             / \
            4   8
           /   / \
          11  13  4
         /  \    / \
        7    2  5   1

Output: 3
Explanation: The paths that sum to 22 are:
1. 5 -> 4 -> 11 -> 2
2. 4 -> 11 -> 7
3. 4 -> 11 -> 2
```

## Constraints

- The number of nodes in the tree is in the range `[0, 1000]`.
- `-10^9 <= Node.val <= 10^9`
- `-1000 <= targetSum <= 1000`

## Solution Approaches

### Approach 1: Brute Force DFS (O(n^2))
```python
def pathSum(root, targetSum):
    if not root:
        return 0
    
    # Count paths starting from current node
    count = count_paths_from(root, targetSum)
    
    # Recurse for left and right subtrees
    count += pathSum(root.left, targetSum)
    count += pathSum(root.right, targetSum)
    
    return count

def count_paths_from(node, target):
    if not node:
        return 0
    
    count = 1 if node.val == target else 0
    
    # Continue path to children
    count += count_paths_from(node.left, target - node.val)
    count += count_paths_from(node.right, target - node.val)
    
    return count
```

### Approach 2: Prefix Sum with Hash Map (O(n))
```python
def pathSum(root, targetSum):
    from collections import defaultdict
    
    prefix_sum = defaultdict(int)
    prefix_sum[0] = 1  # Base case: empty path
    
    count = [0]
    
    def dfs(node, current_sum):
        if not node:
            return
        
        current_sum += node.val
        
        # Check if there's a subpath ending here with targetSum
        count[0] += prefix_sum[current_sum - targetSum]
        
        # Add current sum to prefix sums
        prefix_sum[current_sum] += 1
        
        # Recurse
        dfs(node.left, current_sum)
        dfs(node.right, current_sum)
        
        # Backtrack: remove current sum from prefix sums
        prefix_sum[current_sum] -= 1
    
    dfs(root, 0)
    return count[0]
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Brute Force | O(n^2) | O(h) - recursion |
| Prefix Sum | O(n) | O(h) - recursion + map |

Where n = number of nodes, h = height of tree

## Key Insights

- **Any starting point**: Path can start from any node, not just root
- **Downward only**: Path must go from parent to child
- **Prefix sum technique**: Similar to subarray sum problem in arrays

## Visual Explanation

```
Tree with targetSum = 8:
          10
         /  \
        5   -3
       / \    \
      3   2   11
     / \   \
    3  -2  1

Prefix sum approach:
- At node 5: current_sum = 15, look for 15-8=7 in prefix_sum
- At node 3: current_sum = 18, look for 18-8=10 in prefix_sum
- At node 3 (leaf): current_sum = 21, look for 21-8=13 in prefix_sum
...

Paths found:
1. 5 -> 3 (starting at node 5)
2. 5 -> 2 -> 1 (starting at node 5)
3. -3 -> 11 (starting at node -3)
```

## Algorithm Steps (Prefix Sum)

1. Maintain a hash map of prefix sums encountered
2. For each node, calculate current_sum from root
3. Check if (current_sum - targetSum) exists in map
4. If yes, add count to result
5. Add current_sum to map
6. Recurse for children
7. Backtrack: remove current_sum from map

## Why Prefix Sum Works?

If `prefix[j] - prefix[i] = targetSum`, then the subpath from node i+1 to j sums to targetSum.

## Related Problems

- [Path Sum](problems/09_path_sum.md) - Path must start at root
- [Path Sum II](problems/33_path_sum_ii.md) - Return all paths from root
- [Subarray Sum Equals K](problems/) - Array version of this problem