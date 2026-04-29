# Gas Station

## Problem

Given arrays `gas` and `cost`, return the starting gas station index if you can travel around the circuit once, otherwise return `-1`.

## Input

- `gas`: fuel available at each station
- `cost`: fuel needed to go to next station

## Output

- Start index or `-1`

## Example

```text
Input: gas = [1,2,3,4,5], cost = [3,4,5,1,2]
Output: 3
```

## Intuition

If total gas is enough, a solution exists. When current tank becomes negative, no station in the current segment can be the start.

## Solution

```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1

    start = 0
    tank = 0

    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start = i + 1
            tank = 0

    return start
```

## Complexity

- Time: `O(n)`
- Space: `O(1)`

