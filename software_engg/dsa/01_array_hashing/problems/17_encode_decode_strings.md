# Encode and Decode Strings

## Problem

Design an algorithm to encode a list of strings into one string and decode it back.

## Input

- `strs`: list of strings

## Output

- Encoded string, then decoded list

## Example

```text
Input: ["lint", "code", "love", "you"]
Encoded: "4#lint4#code4#love3#you"
Output: ["lint", "code", "love", "you"]
```

## Intuition

Prefix each string with its length and a delimiter. During decoding, read the length first, then read exactly that many characters.

## Solution

```python
def encode(strs):
    return "".join(f"{len(s)}#{s}" for s in strs)

def decode(s):
    ans = []
    i = 0

    while i < len(s):
        j = i
        while s[j] != "#":
            j += 1

        length = int(s[i:j])
        start = j + 1
        ans.append(s[start:start + length])
        i = start + length

    return ans
```

## Complexity

- Time: `O(total characters)`
- Space: `O(total characters)`

