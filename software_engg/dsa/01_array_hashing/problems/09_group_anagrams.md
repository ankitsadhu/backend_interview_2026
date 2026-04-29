# Group Anagrams

## Problem

Given a list of strings, group the anagrams together.

## Input

- `strs`: list of strings

## Output

- List of anagram groups

## Example

```text
Input: strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
Output: [["eat","tea","ate"], ["tan","nat"], ["bat"]]
```

## Intuition

All anagrams share the same sorted string signature.

## Solution

```python
from collections import defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        key = "".join(sorted(word))
        groups[key].append(word)
    return list(groups.values())
```

## Complexity

- Time: `O(n * k log k)`, where `k` is max word length
- Space: `O(n * k)`

