# Consistency & Consensus

## Consistency Models

### The Spectrum

```
                  Strongest ←──────────────────────→ Weakest
                  (slowest)                          (fastest)

  Linearizability → Sequential → Causal → Eventual
       │                            │         │
  "Real-time         "Some       "Cause      "If no new writes,
   ordering"          total      before       all replicas
                      order"     effect"      eventually converge"
```

---

### Linearizability (Strongest)

**Every operation appears to happen instantaneously at some point between its invocation and response.** The system behaves as if there's only one copy of the data.

```
Timeline:
  Client A:  write(x=1) ────────────────|
  Client B:               read(x) → ?
  
  If write completes before read starts → read MUST return 1
  If they overlap → read returns either 0 or 1 (but once anyone reads 1,
                    all subsequent reads must return 1)

  ✅ write(x=1); write(x=2); read(x) → must return 2 (latest)
  ❌ write(x=1); write(x=2); read(x) → cannot return 1 (stale)
```

**Use cases:** Distributed locks, leader election, unique constraints
**Cost:** High latency (needs coordination across replicas)
**Examples:** ZooKeeper (reads via leader), Spanner, etcd

---

### Sequential Consistency

All operations appear in **some total order** consistent with the **program order** of each individual process. But this order doesn't need to match real-time.

```
Process 1: write(x=1), write(x=2)
Process 2: read(x)=2, read(x)=1    ← INVALID (violates Process 1's order)
Process 2: read(x)=1, read(x)=2    ← VALID (respects Process 1's order)
```

**Difference from linearizability:** No real-time constraint. Operations might not take effect in real-time order.

---

### Causal Consistency

Operations that are **causally related** are seen in the same order by all nodes. **Concurrent operations** can be seen in any order.

```
Causal relationship:
  Alice writes: "Anyone want coffee?" → msg A
  Bob reads msg A, then writes: "Yes please!" → msg B
  
  msg B is causally dependent on msg A
  → Everyone must see msg A before msg B

Concurrent (no causal relation):
  Alice writes: "Anyone want coffee?" → msg A
  Charlie writes: "Nice weather today" → msg C (didn't see msg A)
  
  → Some nodes may see C before A (that's fine)
```

**Use cases:** Social media (comments must appear after the post they reply to)
**Cost:** Moderate (track dependencies, not global ordering)

---

### Eventual Consistency (Weakest)

If no new writes occur, **eventually** all replicas converge to the same value. No ordering guarantees during updates.

```
Write x=1 on Node A
  Node A: x=1
  Node B: x=0  (hasn't received update yet)
  Node C: x=0  (hasn't received update yet)

  ... time passes ...

  Node A: x=1
  Node B: x=1  ✓ converged
  Node C: x=1  ✓ converged
```

**Use cases:** DNS, CDN caches, shopping cart, social media likes/counts
**Cost:** Lowest latency, highest availability
**Examples:** DynamoDB (default), Cassandra, DNS

---

### Read-After-Write Consistency

A user always sees their own writes immediately (but other users may see them with delay).

```
User Alice:
  1. Writes: update profile picture
  2. Reads: sees new profile picture ← MUST succeed

User Bob:
  1. Reads Alice's profile: may see old picture temporarily
```

**Implementation:** Read from leader for your own data, read from follower for others.

---

### Monotonic Read Consistency

Once a user reads a value, they never see an **older** value in subsequent reads.

```
❌ Violation (two reads go to different replicas):
  Read 1 (replica A): x=5
  Read 2 (replica B): x=3  ← Stale! (time went "backwards")

✅ Monotonic reads:
  Read 1: x=5
  Read 2: x=5 or x=6  ← Never older than 5
```

**Implementation:** Sticky sessions (always read from same replica) or version tracking.

---

## Consensus Protocols

### The Consensus Problem

```
Goal: Multiple nodes agree on a single value, even if some nodes crash.

Requirements:
  1. Agreement:     All non-faulty nodes decide the same value
  2. Validity:      The decided value was proposed by some node
  3. Termination:   All non-faulty nodes eventually decide
  4. Integrity:     Each node decides at most once

FLP Impossibility: In a purely asynchronous system with even ONE crash failure,
  consensus is IMPOSSIBLE to guarantee. (Fischer, Lynch, Paterson 1985)

Real systems work around this by using timeouts (partial synchrony) or
  randomization.
```

---

### Raft (Understandable Consensus)

Designed by Diego Ongaro to be **easier to understand** than Paxos. Used by etcd, CockroachDB, TiKV, Consul.

```
┌─────────────────────────────────────────────────────────┐
│                     Raft Cluster                         │
│                                                         │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐      │
│   │  Leader   │ ──→ │ Follower  │     │ Follower  │      │
│   │  (Node A) │ ──→ │ (Node B)  │     │ (Node C)  │      │
│   │           │     │           │     │           │      │
│   │ Handles   │     │ Replicates│     │ Replicates│      │
│   │ ALL writes│     │ from      │     │ from      │      │
│   └──────────┘     │ leader    │     │ leader    │      │
│        ▲            └──────────┘     └──────────┘      │
│        │ All client                                     │
│        │ requests                                       │
│      Client                                             │
└─────────────────────────────────────────────────────────┘
```

#### Three Roles

| Role | Responsibilities |
|------|-----------------|
| **Leader** | Handles all client requests, replicates log entries to followers |
| **Follower** | Passively receives log entries from leader |
| **Candidate** | Follower that has initiated an election |

#### Leader Election

```
1. All nodes start as Followers
2. Each follower has a random election timeout (150-300ms)
3. If timeout expires without hearing from leader → become Candidate
4. Candidate increments term, votes for itself, requests votes from others
5. If majority vote → become Leader
6. Leader sends periodic heartbeats to prevent new elections

Term 1:         [A: Leader] ──heartbeat──→ [B, C: Followers]
                                    ↓ A crashes
Term 2:         [B: Candidate] ──RequestVote──→ [C: votes yes]
                [B: Leader] ──heartbeat──→ [C: Follower]
```

#### Log Replication

```
Client writes "x=5":

1. Leader appends to its log:     [x=5] (uncommitted)
2. Leader sends to followers:     AppendEntries RPC
3. Followers append to their logs: [x=5] (uncommitted)
4. Followers acknowledge
5. Once majority ack:            Leader commits [x=5] ✓
6. Leader responds to client:    Success!
7. Next heartbeat tells followers to commit

Log:
  Leader:   [T1: x=1] [T1: y=2] [T2: x=5] ← committed
  FollowerB: [T1: x=1] [T1: y=2] [T2: x=5] ← committed
  FollowerC: [T1: x=1] [T1: y=2]            ← catching up
```

#### Safety Guarantees

| Property | Guarantee |
|----------|-----------|
| **Election safety** | At most one leader per term |
| **Leader append-only** | Leader never overwrites its log |
| **Log matching** | If two logs have same index+term, all preceding entries match |
| **Leader completeness** | Committed entries always appear in future leaders' logs |

---

### Paxos

The original consensus algorithm by Leslie Lamport. Notoriously difficult to understand but mathematically proven.

```
Three roles:
  Proposer  → proposes values
  Acceptor  → accepts/rejects proposals
  Learner   → learns the chosen value

Two phases:
  Phase 1 (Prepare):
    Proposer → "Prepare(n)" → Acceptors
    Acceptors → "Promise(n)" if n > any previous prepare

  Phase 2 (Accept):
    Proposer → "Accept(n, value)" → Acceptors
    Acceptors → "Accepted" if no higher prepare received
    
  Majority acceptance = value is chosen
```

**Multi-Paxos:** Optimized for a sequence of values (like Raft's log replication). Elects a distinguished proposer (leader) to skip Phase 1 for subsequent rounds.

---

### 2PC (Two-Phase Commit)

**Atomic commit protocol** for distributed transactions. NOT a consensus protocol (has different guarantees).

```
Phase 1 — Prepare:
  Coordinator ──"Can you commit?"──→ Participant A
  Coordinator ──"Can you commit?"──→ Participant B
  
  Participant A ──"Yes (vote commit)"──→ Coordinator
  Participant B ──"Yes (vote commit)"──→ Coordinator

Phase 2 — Commit/Abort:
  If ALL voted "Yes":
    Coordinator ──"COMMIT"──→ All Participants
  If ANY voted "No":
    Coordinator ──"ABORT"──→ All Participants
```

**Problem — Blocking!**
```
What if coordinator crashes after Phase 1?
  → Participants are stuck! They voted "Yes" but don't know the decision.
  → Cannot commit (coordinator might have aborted)
  → Cannot abort (coordinator might have committed)
  → Must WAIT for coordinator to recover ← BLOCKING!
```

### 3PC (Three-Phase Commit)

Adds a **pre-commit** phase to avoid blocking. But doesn't work with **network partitions**.

```
Phase 1: Prepare → vote
Phase 2: Pre-commit → "everyone voted yes, prepare to commit"
Phase 3: Commit → "do it"

If coordinator crashes after Phase 2:
  → Participants see pre-commit → can safely commit on timeout
  (Because pre-commit means everyone voted yes)
```

**In practice:** 2PC is used (with coordinator recovery), not 3PC. Modern systems prefer consensus-based approaches (Raft/Paxos) or Saga patterns.

---

## Quorum

A **quorum** is the minimum number of nodes that must participate in an operation to guarantee consistency.

```
N = total nodes, W = write quorum, R = read quorum

Strong consistency if: W + R > N

Example (N=3):
  W=2, R=2 → 2+2=4 > 3 ✓ (strong consistency)
  W=1, R=3 → 1+3=4 > 3 ✓ (fast writes, slow reads)
  W=3, R=1 → 3+1=4 > 3 ✓ (slow writes, fast reads)
  W=1, R=1 → 1+1=2 ≤ 3 ✗ (eventual consistency)

Write to W=2 nodes:
  Node A: x=5 ✓
  Node B: x=5 ✓
  Node C: x=3 (stale)

Read from R=2 nodes:
  At least one of the R nodes has the latest write
  → Return the value with the latest timestamp
```

### Sloppy Quorum + Hinted Handoff

```
Normal quorum: write must go to W of the N designated nodes
Sloppy quorum: if a designated node is down, write to ANY available node

Node A: x=5 ✓ (designated)
Node B: DOWN  (designated)
Node D: x=5 ✓ (NOT designated — hint stored)

When Node B recovers:
  Node D sends hinted value to Node B → B catches up
  Node D deletes the hint
```

Used by DynamoDB, Cassandra, Riak. Improves **availability** at the cost of not guaranteeing **consistency** (even with W+R>N).

---

## Leader Election

How to choose one node as the leader (coordinator/primary) in a distributed system.

### Bully Algorithm

```
Nodes have IDs. Highest ID wins.

1. Node detects leader is down
2. Node sends ELECTION to all nodes with higher IDs
3. If no response → this node becomes leader (sends COORDINATOR to all)
4. If higher node responds → higher node takes over

Node 1    Node 2    Node 3 (was leader, crashed)    Node 4
  │                                                    │
  │ ──ELECTION──→ Node 2                               │
  │ ──ELECTION──→ Node 4                               │
  │         Node 2 ──ELECTION──→ Node 4                │
  │                                     Node 4 ──OK──→ │
  │                                     Node 4: "I'm leader!"
```

### Using Consensus (Better)

Use Raft/Paxos for leader election → guarantees exactly one leader with consensus.
Used by: etcd, ZooKeeper, CockroachDB.

### Using Distributed Locks

Use a lock service (ZooKeeper, etcd, Redis Redlock) where the lock holder is the leader.

```
1. All candidates try to acquire lock "/election/leader"
2. Winner holds the lock = leader
3. Leader holds lock with TTL (renews periodically)
4. If leader crashes → lock expires → new election
```

---

## Split Brain

**Split brain** = two or more parts of the system believe they are the leader simultaneously.

```
Network partition:
  ┌───────────┐     X     ┌───────────┐
  │ Node A     │  ──/X/──  │ Node C     │
  │ (Leader!)  │     X     │ (Leader!)  │
  │ Node B     │           │ Node D     │
  └───────────┘           └───────────┘
  
  Both partitions elect their own leader
  → Two leaders accepting writes → data divergence → DISASTER
```

**Prevention:**
1. **Quorum-based election:** Leader needs majority → only one partition can have majority
2. **Fencing tokens:** Monotonically increasing token for each leader. Storage rejects operations with old tokens.
3. **STONITH:** "Shoot The Other Node In The Head" — forcefully shut down the other leader (used in database clusters).

---

## Interview Questions — Consistency & Consensus

### Q1: Explain linearizability vs eventual consistency.

| Aspect | Linearizability | Eventual Consistency |
|--------|----------------|---------------------|
| Guarantee | Reads always return the latest written value | Reads may return stale values temporarily |
| Ordering | Real-time ordering of all operations | No ordering guarantees |
| Performance | High latency (coordination needed) | Low latency (no coordination) |
| Availability | Lower (rejects during partition) | Higher (always responds) |
| Use case | Bank balances, locks, elections | Social media likes, DNS, CDN |

### Q2: How does Raft handle leader failure?

1. Leader stops sending heartbeats
2. Follower's election timeout expires (random 150-300ms)
3. Follower becomes **Candidate**, increments term, votes for itself
4. Sends `RequestVote` to all other nodes
5. If receives majority votes → becomes new **Leader**
6. Starts sending heartbeats to suppress other elections

**Safety:** A candidate with an outdated log cannot win election (voters reject if candidate's log is behind theirs).

### Q3: What is the difference between 2PC and Raft?

| Aspect | 2PC | Raft |
|--------|-----|------|
| **Purpose** | Atomic commit (all commit or all abort) | Consensus (agree on sequence of values) |
| **Coordinator** | Single coordinator (SPOF without recovery) | Elected leader (auto-failover) |
| **Fault tolerance** | Blocks if coordinator crashes | Tolerates minority node failures |
| **Use case** | Distributed transactions | Replicated state machines, leader election |

### Q4: What is a quorum and why is W + R > N important?

A quorum ensures that any read sees at least one node with the latest write. With N=5, W=3, R=3: any 3 write nodes and 3 read nodes must overlap by at least 1 node (since 3+3=6 > 5). That overlapping node has the latest value.
