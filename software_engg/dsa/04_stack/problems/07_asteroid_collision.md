# Asteroid Collision

## Problem

Given asteroids represented by integers, positive values move right and negative values move left. When two asteroids collide, the smaller one explodes. Return the state after all collisions.

## Input

- `asteroids`: list of integers

## Output

- Remaining asteroids

## Example

```text
Input: asteroids = [5,10,-5]
Output: [5,10]
```

## Intuition

Only a right-moving asteroid on the stack can collide with a new left-moving asteroid.

## Solution

```python
def asteroid_collision(asteroids):
    stack = []

    for asteroid in asteroids:
        alive = True

        while alive and asteroid < 0 and stack and stack[-1] > 0:
            if stack[-1] < -asteroid:
                stack.pop()
                continue
            if stack[-1] == -asteroid:
                stack.pop()
            alive = False

        if alive:
            stack.append(asteroid)

    return stack
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

