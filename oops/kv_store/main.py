# -*- coding: utf-8 -*-
"""
main.py  --  Demo for in-memory KV Store (TTL + LRU)
Run:  python -m kv_store.main
"""

import time
import threading
from kv_store.store import KVStore


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ─────────────────────────────────────────────────────────────
# 1. Basic set / get / delete
# ─────────────────────────────────────────────────────────────
section("1. BASIC SET / GET / DELETE")

kv = KVStore(capacity=5)

kv.set("name",    "Alice")
kv.set("lang",    "Python")
kv.set("company", "Google")

print(f"  get('name')    = {kv.get('name')}")
print(f"  get('lang')    = {kv.get('lang')}")
print(f"  get('missing') = {kv.get('missing', 'NOT FOUND')}")

# dict-style operators
kv["score"] = 99
print(f"  kv['score']    = {kv['score']}")
print(f"  'name' in kv   = {'name' in kv}")

kv.delete("lang")
print(f"  after delete('lang'): get = {kv.get('lang', 'GONE')}")


# ─────────────────────────────────────────────────────────────
# 2. TTL Expiry
# ─────────────────────────────────────────────────────────────
section("2. TTL EXPIRY")

kv.set("session", "tok-abc123", ttl=1.5)   # expires in 1.5 s
val, remaining = kv.get_with_ttl("session")
print(f"  Immediately: value={val!r}  remaining_ttl={remaining:.3f}s")

time.sleep(0.8)
val, remaining = kv.get_with_ttl("session")
print(f"  After 0.8s : value={val!r}  remaining_ttl={remaining:.3f}s")

time.sleep(0.8)   # total ~1.6 s — should be expired
val, remaining = kv.get_with_ttl("session")
print(f"  After 1.6s : value={val!r}  remaining_ttl={remaining}  (expired)")

print(f"  'session' in kv = {'session' in kv}")


# ─────────────────────────────────────────────────────────────
# 3. persist() — remove TTL, make key immortal
# ─────────────────────────────────────────────────────────────
section("3. PERSIST (REMOVE TTL)")

kv.set("token", "Bearer xyz", ttl=2.0)
print(f"  TTL before persist: {kv.ttl('token'):.3f}s")
kv.persist("token")
print(f"  TTL after  persist: {kv.ttl('token')}  (None = immortal)")
time.sleep(2.1)
print(f"  After 2.1s  still there: {kv.get('token')!r}")


# ─────────────────────────────────────────────────────────────
# 4. LRU Eviction
# ─────────────────────────────────────────────────────────────
section("4. LRU EVICTION (capacity=4)")

cache = KVStore(capacity=4)
for i in range(1, 5):
    cache.set(f"k{i}", f"v{i}")
print(f"  Keys (MRU->LRU): {cache.keys()}")     # k4 k3 k2 k1

# Access k1 to make it MRU
_ = cache.get("k1")
print(f"  After get(k1)  : {cache.keys()}")     # k1 k4 k3 k2

# Insert k5 — should evict k2 (LRU)
cache.set("k5", "v5")
print(f"  After set(k5)  : {cache.keys()}")     # k5 k1 k4 k3  (k2 evicted)
print(f"  k2 evicted?    : {cache.get('k2', 'EVICTED')}")


# ─────────────────────────────────────────────────────────────
# 5. Default TTL (store-wide)
# ─────────────────────────────────────────────────────────────
section("5. DEFAULT TTL (store-wide)")

short_cache = KVStore(capacity=10, default_ttl=1.0)
short_cache.set("a", 1)
short_cache.set("b", 2)
short_cache.set("c", 3, ttl=10.0)   # override: lives 10 s

print(f"  Immediately: a={short_cache.get('a')} b={short_cache.get('b')} c={short_cache.get('c')}")
time.sleep(1.1)
print(f"  After 1.1s : a={short_cache.get('a', 'EXP')} "
      f"b={short_cache.get('b', 'EXP')} c={short_cache.get('c', 'EXP')}")
print(f"  Size now   : {short_cache.size()}")   # only 'c' survives


# ─────────────────────────────────────────────────────────────
# 6. Thread-Safety Test
# ─────────────────────────────────────────────────────────────
section("6. THREAD SAFETY (10 writers + 5 readers)")

shared = KVStore(capacity=20)
errors: list[str] = []

def writer(thread_id: int) -> None:
    for i in range(50):
        try:
            shared.set(f"key-{thread_id}-{i}", thread_id * 100 + i, ttl=5.0)
        except Exception as e:
            errors.append(str(e))

def reader(thread_id: int) -> None:
    for i in range(50):
        try:
            shared.get(f"key-{thread_id}-{i}")
        except Exception as e:
            errors.append(str(e))

threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
threads += [threading.Thread(target=reader, args=(i,)) for i in range(5)]

for t in threads: t.start()
for t in threads: t.join()

if errors:
    print(f"  [FAIL] {len(errors)} errors: {errors[:3]}")
else:
    print(f"  [PASS] 15 threads finished with 0 errors")
    print(f"  Final size (capped at 20): {shared.size()}")


# ─────────────────────────────────────────────────────────────
# 7. update_ttl
# ─────────────────────────────────────────────────────────────
section("7. UPDATE TTL ON EXISTING KEY")

kv.set("refresh_token", "rt-abc", ttl=2.0)
print(f"  Initial TTL : {kv.ttl('refresh_token'):.3f}s")
time.sleep(0.5)
kv.update_ttl("refresh_token", 5.0)   # reset to 5 s
print(f"  After reset : {kv.ttl('refresh_token'):.3f}s")


# ─────────────────────────────────────────────────────────────
# 8. Stats Report
# ─────────────────────────────────────────────────────────────
section("8. STATS REPORT")

report = cache.stats()
for k, v in report.items():
    print(f"  {k:<20} = {v}")


# ─────────────────────────────────────────────────────────────
# 9. Edge Cases
# ─────────────────────────────────────────────────────────────
section("9. EDGE CASES")

# None as a valid value
kv.set("null_val", None)
print(f"  get('null_val')  = {kv.get('null_val', 'MISSING')!r}  (expected: None)")

# 0 and False as valid values
kv.set("zero",  0)
kv.set("false", False)
print(f"  get('zero')   = {kv.get('zero',  'MISSING')!r}")
print(f"  get('false')  = {kv.get('false', 'MISSING')!r}")

# KeyError on dict-style access
try:
    _ = kv["nonexistent"]
except KeyError as e:
    print(f"  kv['nonexistent'] -> KeyError({e})")

print("\n  All scenarios completed successfully.")
