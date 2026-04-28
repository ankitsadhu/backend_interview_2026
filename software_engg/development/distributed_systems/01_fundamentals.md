# Distributed Systems Fundamentals

## What is a Distributed System?

A **distributed system** is a collection of independent computers that appears to its users as a single coherent system.

> *"A distributed system is one in which the failure of a computer you didn't even know existed can render your own computer unusable."* — Leslie Lamport

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Node A   │ ←→  │  Node B   │ ←→  │  Node C   │
│ (Service) │     │ (Service) │     │ (Service) │
└──────────┘     └──────────┘     └──────────┘
      ↕                ↕                ↕
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Node D   │ ←→  │  Node E   │ ←→  │  Node F   │
│   (DB)    │     │  (Cache)  │     │  (Queue)  │
└──────────┘     └──────────┘     └──────────┘
         Network (unreliable, asynchronous)
```

### Why Distribute?

| Reason | Description |
|--------|-------------|
| **Scalability** | Handle more load than a single machine can |
| **Availability** | Continue operating when some nodes fail |
| **Latency** | Serve users from geographically closer nodes |
| **Fault Tolerance** | No single point of failure |
| **Regulatory** | Data residency requirements (GDPR) |

### The Core Challenge

```
In a single-machine system:
  - Function call → always returns or crashes
  - Shared memory → instant, reliable
  - Clock → single, accurate

In a distributed system:
  - Network call → may never return (timeout? lost? slow?)
  - No shared memory → must send messages
  - Clocks → multiple clocks, each drifting independently
```

---

## The 8 Fallacies of Distributed Computing

Coined by L. Peter Deutsch and others at Sun Microsystems. **Assumptions that developers falsely make:**

| # | Fallacy | Reality |
|---|---------|---------|
| 1 | **The network is reliable** | Packets get lost, duplicated, reordered, corrupted |
| 2 | **Latency is zero** | Cross-region calls: 50-200ms. Even local: ~0.5ms |
| 3 | **Bandwidth is infinite** | Serialization, large payloads, network congestion |
| 4 | **The network is secure** | Every network hop is an attack surface |
| 5 | **Topology doesn't change** | Nodes join, leave, move; IPs change |
| 6 | **There is one administrator** | Multiple teams, vendors, cloud providers |
| 7 | **Transport cost is zero** | Serialization, deserialization, encryption have CPU cost |
| 8 | **The network is homogeneous** | Different OS, hardware, protocols, versions |

**Impact:** Each fallacy leads to bugs that only manifest at scale or under failure.

---

## CAP Theorem

Formulated by Eric Brewer. In the presence of a **network partition**, you must choose between:

```
         Consistency
            /\
           /  \
          /    \
         / Pick \
        /  Two   \
       /    (but   \
      /   partitions \
     /   are mandatory)\
    /________╲_________\
 Availability    Partition
                 Tolerance
```

| Property | Meaning |
|----------|---------|
| **Consistency (C)** | Every read returns the most recent write (linearizability) |
| **Availability (A)** | Every request receives a response (no errors, no timeouts) |
| **Partition Tolerance (P)** | System continues despite network partitions |

### The Real Choice: CP vs AP

Since **network partitions are inevitable** in distributed systems, you can't have all three. The practical choice is:

| Choice | Behavior During Partition | Examples |
|--------|--------------------------|----------|
| **CP** | Sacrifices availability — some requests fail/timeout to maintain consistency | ZooKeeper, HBase, MongoDB (w:majority), Spanner |
| **AP** | Sacrifices consistency — returns stale data to remain available | Cassandra, DynamoDB, CouchDB, DNS |

```
Normal operation (no partition): Both C and A are achievable
During partition: Must choose C or A

Example — Bank account:
  CP: Refuse transactions if we can't confirm balance → safe but unavailable
  AP: Allow transactions based on last-known balance → available but might overdraft
```

### CAP Misconceptions

1. **"Pick two"** is misleading — you always need P, so it's really C vs A
2. **Not binary** — it's a spectrum between strong consistency and high availability
3. **Per-operation** — different operations can make different trade-offs
4. **Only applies during partitions** — normally you can have both C and A

---

## PACELC Theorem

An **extension of CAP** by Daniel Abadi that covers the normal (no-partition) case:

```
   If Partition → choose Availability or Consistency (same as CAP)
   Else (normal) → choose Latency or Consistency
```

| System | PAC | ELC |
|--------|-----|-----|
| **DynamoDB, Cassandra** | PA (available during partition) | EL (low latency normally) |
| **MongoDB, HBase** | PC (consistent during partition) | EC (consistent normally) |
| **PNUTS (Yahoo)** | PC | EL (consistent during partition, but trades consistency for latency normally) |
| **Spanner** | PC | EC (strong consistency always, using TrueTime) |

---

## System Models

### Network Models

| Model | Assumption | Reality |
|-------|-----------|---------|
| **Synchronous** | Known upper bound on message delay | LANs (roughly) |
| **Asynchronous** | No bound on message delay | The Internet |
| **Partially Synchronous** | Usually synchronous, occasionally asynchronous | Most real systems |

### Failure Models

```
Increasing severity:
  ┌─────────────────────────────────────────────────┐
  │  Crash-stop     Node stops and never recovers   │
  │  Crash-recovery Node stops, may restart later    │
  │  Omission       Node fails to send/receive msgs  │
  │  Timing         Node responds, but too slowly     │
  │  Byzantine      Node behaves arbitrarily         │
  │                 (bugs, hacking, malicious data)   │
  └─────────────────────────────────────────────────┘
```

| Model | Assumed in | Handling |
|-------|-----------|----------|
| **Crash-stop** | Most distributed DBs | Heartbeats + replacement |
| **Crash-recovery** | Most practical systems | WAL, checkpoints, replay |
| **Byzantine** | Blockchain, military systems | BFT consensus (expensive) |

---

## Types of Failures

### Partial Failures

In a distributed system, **some parts can fail while others work**. This is fundamentally different from a single machine (which either works or doesn't).

```
Scenario: User request → Service A → Service B → Database

Possible failures:
1. Service A crashes → request never reaches B (detectable)
2. Network between A and B drops → A doesn't know if B received the request
3. B processes request but response is lost → A retries → duplicate!
4. B is slow (not failed) → A times out and retries → B processes twice!
5. A crashes after sending to B but before acknowledging user
```

### Failure Detection

```
How do you know a node has failed?

  ┌──────────┐    heartbeat    ┌──────────┐
  │  Node A   │ ──────────→    │  Node B   │
  └──────────┘    every 5s     └──────────┘

  If no heartbeat for 3 intervals (15s):
    → Is B crashed? Is the network broken? Is B just slow?
    → You CAN'T distinguish! (FLP impossibility result)

  Solution: Use timeouts with imperfect failure detection
    → May falsely suspect healthy nodes (false positives)
    → May miss failed nodes temporarily (false negatives)
```

### The Two Generals Problem

```
  Army A ────── Enemy ────── Army B
              (unreliable
               channel)

  Both armies must attack simultaneously to win.
  Army A sends messenger: "Attack at dawn"
  But messenger might be captured!
  
  Even if B acknowledges, A doesn't know if the ACK arrived.
  And B doesn't know if A knows B got the message.
  
  → Infinite chain of confirmations needed
  → IMPOSSIBLE to achieve certainty over unreliable channel
```

**Implication:** You cannot achieve 100% agreement over an unreliable network. Real systems use probabilistic approaches (retries, timeouts, consensus protocols).

---

## Clocks and Time

### Why Time is Hard

```
Node A clock: 10:00:00.000
Node B clock: 10:00:00.150    ← 150ms ahead (clock skew)
Node C clock: 09:59:59.900    ← 100ms behind

Event happens at "the same time" on all nodes:
  A records: 10:00:05.000
  B records: 10:00:05.150
  C records: 10:00:04.900

Question: Which event happened first?
  → Clock ordering ≠ actual ordering!
```

### Physical Clocks

| Type | Accuracy | Use Case |
|------|----------|----------|
| **System clock** (wall clock) | ~1-100ms drift via NTP | Timestamps, display |
| **Monotonic clock** | Precise intervals (within one machine) | Measuring elapsed time |
| **GPS/atomic clock** | ~1-10μs | Google Spanner's TrueTime |

**NTP (Network Time Protocol):** Synchronizes clocks across nodes. Typical accuracy: **1-50ms** over the internet, **<1ms** on a LAN.

> **Never use wall clocks for ordering events across nodes.** Use logical clocks instead.

### Logical Clocks

#### Lamport Timestamps

A simple counter that establishes **partial ordering** of events.

```
Rules:
  1. Each process maintains a counter C
  2. Before each event: C = C + 1
  3. When sending message: attach C to message
  4. When receiving message with timestamp T: C = max(C, T) + 1

Node A:           Node B:
  C=1 (event)
  C=2 (send)──→   C=3 (receive, max(0,2)+1)
                   C=4 (event)
  C=5 (recv) ←──  C=5 (send)
```

**Guarantee:** If event A happened before event B → `C(A) < C(B)`
**Limitation:** If `C(A) < C(B)`, A may or may NOT have happened before B (can't tell concurrent events apart).

#### Vector Clocks

Track causality across all nodes. **Each node maintains a vector of counters** (one per node).

```
System with 3 nodes [A, B, C]:

Node A:   [1,0,0] → [2,0,0] → ──send──→
Node B:                        [0,0,0] → [2,1,0] (recv, max + inc B)
Node C:                                             [0,0,1]

Comparing vectors:
  [2,1,0] vs [0,0,1]
  A > C? No (0 < 1 in position 3)
  C > A? No (0 < 2 in position 1)
  → CONCURRENT events! (Neither happened before the other)
```

**Guarantee:** Can detect both **causal ordering** and **concurrency**.
**Limitation:** Vector size grows with number of nodes (O(n) space).

#### Hybrid Logical Clocks (HLC)

Combines physical timestamps with logical counters. Used by CockroachDB, YugabyteDB.

```
HLC = (physical_time, logical_counter)

- physical_time: wall clock (for human-readable ordering)
- logical_counter: disambiguates events at the same physical time
- Bounded skew: HLC stays close to real time

Benefits:
- Compact (2 values) vs vector clocks (n values)
- Compatible with NTP (respects physical time)
- Can detect causality
```

---

## Idempotency

An operation is **idempotent** if performing it multiple times has the same effect as performing it once.

```
Idempotent:          NOT idempotent:
  SET x = 5           x = x + 1
  DELETE user 123     Transfer $100 from A to B
  PUT /users/123      POST /users (creates new each time)
  HTTP GET             Dequeue message
```

### Why It Matters

In distributed systems, **retries are inevitable** (timeout → retry → was the first request actually processed?).

```
Client ──request──→ Server
Client ──timeout── (no response received)
Client ──retry────→ Server    ← Is this a duplicate?

If operation is idempotent:  no problem!
If NOT idempotent:           double-charge, double-post, etc.
```

### Implementing Idempotency

```
Strategy 1: Idempotency Keys
  - Client generates unique ID for each logical operation
  - Server tracks processed IDs
  - On retry: "Already processed, here's the cached result"

Strategy 2: Conditional Operations
  - Use version numbers / ETags
  - "Update balance to $90 IF current version = 5"
  - Retry with same condition → no effect (version already changed)

Strategy 3: Natural Idempotency
  - Design operations to be naturally idempotent
  - "Set balance to $90" instead of "Subtract $10"
```

---

## Exactly-Once, At-Least-Once, At-Most-Once

| Delivery Guarantee | Meaning | How |
|-------------------|---------|-----|
| **At-most-once** | Send and forget. May be lost. | No retries |
| **At-least-once** | Retry until acknowledged. May duplicate. | Retries + timeout |
| **Exactly-once** | Processed exactly once. The holy grail. | At-least-once + idempotency |

```
At-most-once:       Fire-and-forget (UDP, logging, metrics)
At-least-once:      Retry with deduplication risk (most APIs)
Exactly-once:       At-least-once + idempotent receiver (Kafka with transactions)

"Exactly-once" is technically impossible over unreliable networks.
What we actually achieve: "effectively-once" via idempotent processing.
```

---

## Common Interview Questions — Fundamentals

### Q1: What is the CAP theorem? Give real-world examples.

**CAP:** During a network partition, choose Consistency or Availability.

- **CP example:** A bank system that refuses transactions during network issues rather than risk inconsistency.
- **AP example:** A social media feed that shows slightly stale posts during network issues rather than going offline.

**Key insight:** CAP only constrains behavior during partitions. Normally, you can have both.

---

### Q2: Explain the difference between Lamport timestamps and vector clocks.

| Aspect | Lamport Timestamps | Vector Clocks |
|--------|-------------------|---------------|
| Size | Single integer | Array of N integers |
| Ordering | Partial (if L(A)<L(B), A _might_ be before B) | Partial + concurrency detection |
| Concurrent events | Cannot detect | Can detect |
| Use case | Simple ordering | Conflict detection (Dynamo-style) |

---

### Q3: Why can't you achieve exactly-once delivery?

Due to the **Two Generals Problem:** over an unreliable network, you can't be 100% sure the other side received your message. The best you can do is:
- **At-least-once delivery** (retries) + **idempotent processing** (deduplication)
- This achieves **effectively-once semantics** — the effect happens exactly once, even if the message is delivered multiple times.
