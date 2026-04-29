# Majority Element

## Problem

Given an array `nums`, return the element that appears more than `n / 2` times.

## Input

- `nums`: list of integers

## Output

- Majority element

## Example

```text
Input: nums = [2,2,1,1,1,2,2]
Output: 2
```

## Intuition

Boyer-Moore voting cancels different elements. The majority survives because it appears more than all other elements combined.

## Solution

```python
def majority_element(nums):
    candidate = None
    count = 0

    for num in nums:
        if count == 0:
            candidate = num
        count += 1 if num == candidate else -1

    return candidate
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

