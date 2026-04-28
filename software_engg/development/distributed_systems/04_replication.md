# Replication

## Why Replicate Data?

| Reason | Description |
|--------|-------------|
| **High Availability** | If one node fails, others serve requests |
| **Fault Tolerance** | Data survives node/disk failures |
| **Read Scalability** | Distribute reads across replicas |
| **Latency** | Serve users from geographically closer replicas |

---

## Single-Leader Replication

One node is the **leader** (primary/master). All writes go to the leader, which replicates to **followers** (secondaries/replicas).

```
                     Writes
                       │
                       ▼
                 ┌──────────┐
                 │  Leader    │
                 │ (Primary)  │
                 └──────┬─────┘
                        │ replication
              ┌─────────┼─────────┐
              ▼         ▼         ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Follower │ │ Follower │ │ Follower │
        │    1     │ │    2     │ │    3     │
        └──────────┘ └──────────┘ └──────────┘
              ▲         ▲         ▲
              │         │         │
              └─────────┼─────────┘
                     Reads
```

### Synchronous vs Asynchronous Replication

```
SYNCHRONOUS:
  Client ──write──→ Leader ──replicate──→ Follower 1 ──ACK──→ Leader ──ACK──→ Client
  ✅ Follower guaranteed up-to-date
  ❌ Write latency = Leader + slowest follower
  ❌ If follower is down, writes block

ASYNCHRONOUS:
  Client ──write──→ Leader ──ACK──→ Client       (immediate!)
                    Leader ──replicate──→ Followers (in background)
  ✅ Fast writes (no waiting for followers)
  ❌ Follower may be behind (replication lag)
  ❌ Data loss if leader crashes before replicating

SEMI-SYNCHRONOUS:
  One follower is synchronous (guaranteed up-to-date)
  Other followers are asynchronous
  ✅ Balance of durability and performance
  Used by: MySQL semi-sync, MongoDB w:majority
```

### Replication Lag

```
Write to leader at T=0: x=5
Follower receives at T=200ms: x=5

During that 200ms window:
  Read from leader:   x=5 ✓
  Read from follower: x=3 (stale!) ✗

Replication lag = time between write on leader and availability on follower
Typical: <1 second on a healthy system
Worst case: seconds to minutes (under load, network issues)
```

#### Consistency Issues from Replication Lag

```
1. Read-after-write inconsistency:
   User writes profile update → reads from replica → sees OLD data!
   Fix: Read user's own data from leader

2. Monotonic read violation:
   Read 1 from Replica A: x=5
   Read 2 from Replica B: x=3  (Replica B is behind)
   Fix: Sticky sessions (always read from same replica)

3. Causality violation:
   User A posts comment → User B sees reply before the original comment
   Fix: Causal consistency with version vectors
```

### Handling Leader Failure (Failover)

```
1. Detect leader failure (heartbeat timeout)
2. Choose new leader (most up-to-date follower)
3. Reconfigure system (clients redirect to new leader)

Challenges:
  - Lost writes: async followers may miss recent writes from old leader
  - Split brain: old leader comes back, thinks it's still leader → TWO leaders!
  - Client confusion: which is the real leader during transition?

Solutions:
  - Consensus-based election (Raft) → exactly one leader
  - Fencing tokens → storage rejects outdated leaders
  - Epoch numbers → monotonically increasing leader version
```

---

## Multi-Leader Replication

Multiple nodes accept writes. Each leader replicates to all other leaders.

```
┌──────────┐         ┌──────────┐
│ Leader A  │ ←─────→ │ Leader B  │
│ (DC East) │   sync  │ (DC West) │
└──────────┘         └──────────┘
     ↕                     ↕
┌──────────┐         ┌──────────┐
│ Followers │         │ Followers │
└──────────┘         └──────────┘
```

### When to Use Multi-Leader

| Scenario | Why Multi-Leader |
|----------|-----------------|
| **Multi-datacenter** | Each DC has a leader → writes don't cross WAN |
| **Offline-capable** | Each device is a "leader" (e.g., calendar apps) |
| **Collaborative editing** | Multiple users edit simultaneously (Google Docs) |

### The Write Conflict Problem

```
User A (via Leader 1): SET name = "Alice"    at T=1
User B (via Leader 2): SET name = "Bob"      at T=1

Both succeed locally. When leaders sync:
  Conflict! name = "Alice" or "Bob"?
```

### Conflict Resolution Strategies

| Strategy | Description | Trade-off |
|----------|-------------|-----------|
| **Last-Writer-Wins (LWW)** | Highest timestamp wins | Simple but loses data (not truly conflict-free) |
| **Per-field merge** | Merge non-conflicting fields | Works for some cases |
| **Custom handler** | Application-specific logic | Most flexible, most complex |
| **CRDTs** | Mathematically conflict-free data types | Auto-merge, limited operations |
| **Operational Transform** | Transform concurrent operations | Google Docs approach |

---

## Leaderless Replication

**No designated leader**. Any node accepts writes. Reads from multiple nodes.

```
Client ──write──→ Node A ✓
       ──write──→ Node B ✓
       ──write──→ Node C ✗ (temporarily down)

Client ──read──→ Node A: x=5
       ──read──→ Node B: x=5
       ──read──→ Node C: x=3 (stale)
       
       → Return x=5 (latest version from quorum)
```

Used by: Dynamo (Amazon), Cassandra, Riak, Voldemort

### Read Repair and Anti-Entropy

```
READ REPAIR:
  Client reads from 3 nodes → detects Node C is stale
  Client writes updated value back to Node C
  → Passive repair on each read

ANTI-ENTROPY:
  Background process constantly compares replicas
  Detects and fixes inconsistencies
  → Active repair (eventually all nodes converge)
```

### Conflict Resolution in Leaderless Systems

```
Concurrent writes to same key:
  Node A: x=5 (version [A:1, B:0])
  Node B: x=7 (version [A:0, B:1])

  Vector clocks detect: these are CONCURRENT (neither dominates)
  
  Resolution options:
  1. LWW (Last-Writer-Wins) — pick one, discard other ← LOSSY
  2. Siblings — return BOTH values, let application merge ← SAFE
  3. CRDTs — automatically merge without conflicts ← ELEGANT
```

---

## CRDTs (Conflict-free Replicated Data Types)

Data structures that can be replicated across nodes and **automatically merged** without conflicts.

```
CRDT Property: 
  merge(A, B) = merge(B, A)             (commutative)
  merge(A, merge(B, C)) = merge(merge(A, B), C)  (associative)
  merge(A, A) = A                        (idempotent)
```

### Common CRDTs

| CRDT | Type | How It Works |
|------|------|-------------|
| **G-Counter** | Counter | Each node has its own counter. Total = sum of all. |
| **PN-Counter** | Counter | Separate G-Counter for increments and decrements |
| **G-Set** | Set | Elements can only be added (grow-only) |
| **OR-Set** | Set | Add and remove with unique tags per operation |
| **LWW-Register** | Register | Last-Writer-Wins based on timestamp |
| **LWW-Element-Set** | Set | Add/remove with timestamps, latest wins |
| **MV-Register** | Register | Multi-value (keeps all concurrent writes) |

```
G-Counter Example (3 nodes):
  Node A: [A:3, B:0, C:0]    → total = 3
  Node B: [A:0, B:5, C:0]    → total = 5
  Node C: [A:0, B:0, C:2]    → total = 2

  Merge: [A:3, B:5, C:2]     → total = 10
  (take max of each position)
  
  No conflicts, no coordination!
```

**Used by:** Redis (CRDT-based replication), Riak, Automerge, Yjs (collaborative editing)

---

## Chain Replication

A specialized approach where nodes form a **chain** for replication.

```
Client ──write──→ [Head] ──→ [Middle] ──→ [Tail] ──ACK──→ Client
Client ──read────────────────────────────→ [Tail]

Head: receives writes, forwards to next
Middle: forwards writes
Tail: commits writes, serves reads

✅ Strong consistency (reads always from fully-replicated tail)
✅ High read throughput (dedicated tail for reads)
❌ Write latency = sum of all node delays (chain length)
❌ Single node failure requires chain repair
```

Used by: Azure Storage, HDFS (variant), Microsoft's internal systems.

---

## Interview Questions — Replication

### Q1: What are the trade-offs between sync and async replication?

| Aspect | Synchronous | Asynchronous |
|--------|------------|--------------|
| **Durability** | ✅ Write on N nodes before ACK | ❌ May lose data if leader crashes |
| **Latency** | ❌ Slow (wait for slowest replica) | ✅ Fast (immediate ACK) |
| **Availability** | ❌ Blocked if replica is down | ✅ Works even if replicas are down |
| **Consistency** | ✅ Replicas always up-to-date | ❌ Replication lag |

### Q2: How do you handle a write conflict in multi-leader replication?

1. **Prevention:** Avoid conflicts by routing writes for the same key to the same leader
2. **Detection:** Compare version vectors or timestamps when syncing
3. **Resolution:** LWW (simple but lossy), application-level merge, or CRDTs (auto-merge)

### Q3: What is the difference between single-leader, multi-leader, and leaderless?

| Aspect | Single-Leader | Multi-Leader | Leaderless |
|--------|--------------|-------------|-----------|
| Write target | 1 node | Multiple leaders | Any node |
| Conflict handling | No write conflicts | Must resolve conflicts | Must resolve conflicts |
| Latency | Writes go to leader (may cross WAN) | Local writes per DC | Writes to nearest nodes |
| Complexity | Simple | Moderate | Complex |
| Examples | PostgreSQL, MongoDB | CouchDB, Google Docs | Cassandra, DynamoDB |

### Q4: What is read repair?

When a client reads from multiple replicas and finds that one has stale data, it **writes the latest value back** to the stale replica. This "heals" the inconsistency opportunistically on each read, without needing a background process.
