# Bulls and Cows

## Problem

Given strings `secret` and `guess`, return a hint in the form `"xAyB"` where `x` is bulls and `y` is cows.

## Input

- `secret`: digit string
- `guess`: digit string

## Output

- Hint string

## Example

```text
Input: secret = "1807", guess = "7810"
Output: "1A3B"
```

## Intuition

Bulls are exact matches. For non-matching positions, count shared digits to get cows.

## Solution

```python
from collections import Counter

def get_hint(secret, guess):
    bulls = 0
    secret_rest = []
    guess_rest = []

    for s, g in zip(secret, guess):
        if s == g:
            bulls += 1
        else:
            secret_rest.append(s)
            guess_rest.append(g)

    count = Counter(secret_rest)
    cows = 0
    for digit in guess_rest:
        if count[digit] > 0:
            cows += 1
            count[digit] -= 1

    return f"{bulls}A{cows}B"
```

## Complexity

- Time: `O(n)`
- Space: `O(1)` for digits

