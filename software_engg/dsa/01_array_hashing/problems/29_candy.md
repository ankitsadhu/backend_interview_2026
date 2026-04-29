# Candy

## Problem

Given ratings of children, give each child at least one candy. Children with a higher rating than an adjacent child must get more candies. Return the minimum candies needed.

## Input

- `ratings`: list of integers

## Output

- Minimum candy count

## Example

```text
Input: ratings = [1,0,2]
Output: 5
```

## Intuition

Left-to-right handles higher than left neighbor. Right-to-left handles higher than right neighbor.

## Solution

```python
def candy(ratings):
    n = len(ratings)
    candies = [1] * n

    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1

    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)

    return sum(candies)
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

