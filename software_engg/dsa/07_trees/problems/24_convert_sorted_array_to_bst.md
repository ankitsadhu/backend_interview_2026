# Convert Sorted Array to Binary Search Tree

## Question

Given an integer array `nums` where the elements are sorted in **ascending order**, convert it to a **height-balanced** binary search tree (BST).

A **height-balanced** binary tree is defined as a binary tree in which the depth of the two subtrees of every node never differs by more than 1.

## Examples

### Example 1
```
Input: nums = [-10,-3,0,5,9]

Output: [0,-3,9,-10,null,5]
Explanation: One possible balanced BST is:
          0
         / \
       -3   9
       /   /
     -10  5

Another valid output: [0,-10,5,null,-3,null,9]
         0
        / \
      -10  5
        \   \
        -3  9
```

### Example 2
```
Input: nums = [1,3]

Output: [3,1]
Explanation: One possible balanced BST is:
        3
       /
      1

Or: [1,null,3]
      1
       \
        3
```

### Example 3
```
Input: nums = []
Output: []
```

## Constraints

- `1 <= nums.length <= 10^4`
- `-10^4 <= nums[i] <= 10^4`
- `nums` is sorted in a **strictly increasing order**.

## Solution Approaches

### Approach: Recursive (Divide and Conquer)
```python
def sortedArrayToBST(nums):
    if not nums:
        return None
    
    # Find the middle element to make it root
    mid = len(nums) // 2
    
    # Create root node
    root = TreeNode(nums[mid])
    
    # Recursively build left and right subtrees
    root.left = sortedArrayToBST(nums[:mid])
    root.right = sortedArrayToBST(nums[mid+1:])
    
    return root
```

### Approach: Recursive with Indices (More Efficient)
```python
def sortedArrayToBST(nums):
    def build(left, right):
        if left > right:
            return None
        
        # Find middle element
        mid = (left + right) // 2
        
        # Create node
        node = TreeNode(nums[mid])
        
        # Build left and right subtrees
        node.left = build(left, mid - 1)
        node.right = build(mid + 1, right)
        
        return node
    
    return build(0, len(nums) - 1)
```

## Complexity Analysis

| Approach | Time Complexity | Space Complexity |
|----------|-----------------|------------------|
| Recursive (slicing) | O(n log n) | O(log n) - recursion |
| Recursive (indices) | O(n) | O(log n) - recursion |

Where n = number of elements in array

## Key Insights

- **Middle element as root**: Ensures balanced tree
- **Divide and conquer**: Left half becomes left subtree, right half becomes right subtree
- **Inorder traversal**: The sorted array is essentially the inorder traversal of the BST

## Visual Explanation

```
nums = [-10, -3, 0, 5, 9]

Step 1: mid = 2, root = 0
        [-10, -3]  0  [5, 9]

Step 2: Build left subtree from [-10, -3]
        mid = 1, root = -3
        [-10]  -3  []

Step 3: Build right subtree from [5, 9]
        mid = 1, root = 9
        [5]  9  []

Final tree:
          0
         / \
       -3   9
       /   /
     -10  5
```

## Algorithm Steps

1. Find the middle element of the array
2. Make it the root of the current subtree
3. Recursively build left subtree from left half
4. Recursively build right subtree from right half
5. Return the root

## Why Middle Element?

Choosing the middle element ensures:
- **Balanced tree**: Equal (or nearly equal) nodes on both sides
- **BST property**: All left elements < mid < all right elements
- **Height balance**: Depth difference between subtrees ≤ 1

## Related Problems

- [Validate Binary Search Tree](problems/18_validate_binary_search_tree.md)
- [Convert BST to Greater Tree](problems/26_convert_bst_to_greater_tree.md)
- [Balance a Binary Search Tree](problems/) - Convert any BST to balanced BST