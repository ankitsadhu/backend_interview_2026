# Restore IP Addresses

## Problem

Given a string containing only digits, return all possible valid IP addresses that can be formed by inserting three dots.

## Input

- `s`: digit string

## Output

- List of valid IP address strings

## Example

```text
Input: s = "25525511135"
Output: ["255.255.11.135", "255.255.111.35"]
```

## Intuition

An IP has exactly four parts. Each part must be from `0` to `255`, and cannot have leading zeroes unless it is exactly `"0"`.

## Solution

```python
def restore_ip_addresses(s):
    ans = []

    def valid(part):
        if len(part) > 1 and part[0] == "0":
            return False
        return 0 <= int(part) <= 255

    def backtrack(index, parts):
        if len(parts) == 4:
            if index == len(s):
                ans.append(".".join(parts))
            return

        remaining_parts = 4 - len(parts)
        remaining_chars = len(s) - index
        if remaining_chars < remaining_parts or remaining_chars > remaining_parts * 3:
            return

        for size in range(1, 4):
            part = s[index:index + size]
            if index + size <= len(s) and valid(part):
                parts.append(part)
                backtrack(index + size, parts)
                parts.pop()

    backtrack(0, [])
    return ans
```

## Complexity

- Time: `O(1)` because there are at most four segments of length three
- Space: `O(1)` excluding output

