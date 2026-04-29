# Car Fleet

## Problem

Given a target, positions, and speeds of cars, return how many car fleets arrive at the target.

## Input

- `target`: destination
- `position`: car positions
- `speed`: car speeds

## Output

- Number of fleets

## Example

```text
Input: target = 12, position = [10,8,0,5,3], speed = [2,4,1,1,3]
Output: 3
```

## Intuition

Sort cars by position from closest to farthest. A farther car joins the fleet ahead if it reaches the target no sooner than that fleet.

## Solution

```python
def car_fleet(target, position, speed):
    cars = sorted(zip(position, speed), reverse=True)
    fleets = 0
    slowest_time = 0

    for pos, spd in cars:
        time = (target - pos) / spd
        if time > slowest_time:
            fleets += 1
            slowest_time = time

    return fleets
```

## Complexity

- Time: `O(n log n)`
- Space: `O(n)`

