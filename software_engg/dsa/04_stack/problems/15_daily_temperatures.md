# Daily Temperatures

## Problem

Given daily temperatures, return how many days each day must wait until a warmer temperature. Use `0` if no warmer day exists.

## Input

- `temperatures`: list of integers

## Output

- Wait days for each index

## Example

```text
Input: temperatures = [73,74,75,71,69,72,76,73]
Output: [1,1,4,2,1,1,0,0]
```

## Intuition

Store indices with unresolved warmer days. A warmer current temperature resolves colder previous indices.

## Solution

```python
def daily_temperatures(temperatures):
    ans = [0] * len(temperatures)
    stack = []

    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            prev = stack.pop()
            ans[prev] = i - prev
        stack.append(i)

    return ans
```

## Complexity

- Time: `O(n)`
- Space: `O(n)`

