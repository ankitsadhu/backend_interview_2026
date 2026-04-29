# Majority Element II

## Problem

Given an array `nums`, return all elements that appear more than `n / 3` times.

## Input

- `nums`: list of integers

## Output

- Elements appearing more than `n / 3` times

## Example

```text
Input: nums = [3, 2, 3]
Output: [3]
```

## Intuition

There can be at most two elements appearing more than `n / 3` times. Track two candidates, then verify them.

## Solution

```python
def majority_element(nums):
    cand1 = cand2 = None
    count1 = count2 = 0

    for num in nums:
        if num == cand1:
            count1 += 1
        elif num == cand2:
            count2 += 1
        elif count1 == 0:
            cand1, count1 = num, 1
        elif count2 == 0:
            cand2, count2 = num, 1
        else:
            count1 -= 1
            count2 -= 1

    ans = []
    for candidate in (cand1, cand2):
        if candidate is not None and nums.count(candidate) > len(nums) // 3:
            ans.append(candidate)

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

