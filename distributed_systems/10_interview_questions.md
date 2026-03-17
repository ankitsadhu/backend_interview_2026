# Distributed Systems Interview Questions

> Comprehensive question bank covering beginner to advanced topics, rapid-fire, and system design scenarios.

---

## 🟢 Beginner Level

### Q1: What is a distributed system? Why not just use one big server?

A distributed system is a collection of independent computers that appear as a single system to users.

**Why distribute:**
- Single server has CPU, RAM, and storage limits
- Single server is a single point of failure
- Users across the globe need low latency
- Regulatory requirements (data residency)

**The cost:** Distributed systems are significantly more complex (network failures, partial failures, consistency challenges).

---

### Q2: What is the CAP theorem?

During a **network partition**, you must choose between:
- **Consistency:** Every read returns the latest write
- **Availability:** Every request gets a response

You can't have both during a partition. Examples:
- **CP:** Bank systems (refuse transactions if uncertain)
- **AP:** Social media (show stale data rather than going offline)

---

### Q3: What is eventual consistency?

If no new writes occur, all replicas will **eventually** converge to the same value. During updates, different replicas may return different values temporarily.

Used by: DNS, CDN caches, DynamoDB (default), Cassandra.

Key insight: "Eventually" can be milliseconds or hours — it's not a timing guarantee.

---

### Q4: What are the delivery guarantees for messages?

| Guarantee | Meaning | Implementation |
|-----------|---------|----------------|
| At-most-once | May be lost, never duplicated | Fire and forget |
| At-least-once | Never lost, may be duplicated | Retry until ACK |
| Exactly-once | Never lost, never duplicated | At-least-once + idempotent consumer |

---

### Q5: What is idempotency and why does it matter?

An operation is idempotent if executing it multiple times has the same effect as executing it once.

**Why it matters:** In distributed systems, retries are inevitable (timeouts, network issues). If operations aren't idempotent, retries cause duplicates (double charges, double posts).

**Example:** `SET balance = 100` is idempotent. `ADD 100 to balance` is NOT.

---

## 🟡 Intermediate Level

### Q6: Explain single-leader vs leaderless replication.

| Aspect | Single-Leader | Leaderless |
|--------|--------------|-----------|
| Writes | Go to leader only | Go to any node (quorum) |
| Consistency | Strong (from leader) | Tunable (W + R > N for strong) |
| Failover | Election needed (downtime) | No single failure point |
| Conflicts | None (one writer) | Possible (concurrent writes) |
| Examples | PostgreSQL, MongoDB | Cassandra, DynamoDB |

---

### Q7: What is consistent hashing?

A technique for distributing data across nodes that **minimizes data movement** when nodes are added or removed. Each node and key maps to a position on a hash ring. Keys are assigned to the next node clockwise.

When a node is added, only ~1/N of keys move (vs ALL keys in `hash % N`).

**Virtual nodes** improve balance by giving each physical node multiple positions on the ring.

---

### Q8: What is the Saga pattern?

A pattern for managing distributed transactions without 2PC. A saga is a sequence of local transactions with compensating actions for rollback.

```
Success: T1 → T2 → T3 → Done
Failure: T1 → T2 → T3(FAIL) → C2 → C1 → Rolled back
```

Two styles:
- **Choreography:** Services react to events (decoupled, hard to track)
- **Orchestration:** Central coordinator directs the flow (clear, single point)

---

### Q9: Explain the Circuit Breaker pattern.

Three states:
1. **CLOSED:** Normal operation, requests pass through. Count failures.
2. **OPEN:** Too many failures → reject all requests immediately (fast failure, no downstream load)
3. **HALF-OPEN:** After timeout, allow limited requests to test if downstream recovered.

Prevents cascading failures when a downstream service is unhealthy.

---

### Q10: What is the difference between synchronous and asynchronous communication?

| Aspect | Synchronous | Asynchronous |
|--------|------------|--------------|
| Coupling | Tight (both services must be running) | Loose (producer doesn't know consumer) |
| Response | Immediate | Delayed (or none) |
| Example | REST API call | Message queue (Kafka, RabbitMQ) |
| Failure impact | Caller blocked if callee is down | Messages buffered in queue |
| Use case | User-facing requests | Background processing, event-driven |

---

### Q11: How does Raft consensus work?

1. Cluster of nodes with one **Leader** and multiple **Followers**
2. Leader handles all client writes, replicates log entries to followers
3. **Majority acknowledgment** = entry committed (e.g., 3 of 5 nodes)
4. If leader crashes → **election timeout** expires → follower becomes Candidate → requests votes
5. Candidate with most up-to-date log and majority votes → new Leader
6. Typical failover: ~10-12 seconds

---

## 🔴 Advanced Level

### Q12: Compare Kafka and RabbitMQ. When to use each?

| Feature | Kafka | RabbitMQ |
|---------|-------|----------|
| Model | Distributed log | Message broker |
| Retention | Keeps messages (configurable) | Deletes on consumption |
| Throughput | Very high (100K+ msg/s) | High (50K+ msg/s) |
| Ordering | Per-partition guarantee | Per-queue FIFO |
| Replay | ✅ Re-read from any offset | ❌ Once consumed, gone |
| Routing | Topic → partition (key-based) | Exchanges (direct, topic, fanout, headers) |
| Best for | Event streaming, data pipelines | Task queues, RPC, complex routing |

---

### Q13: How would you prevent distributed deadlocks?

1. **Lock ordering:** Always acquire locks in the same global order
2. **Timeouts:** Set timeouts on all lock acquisitions
3. **Deadlock detection:** Build wait-for graph, detect cycles, abort one transaction
4. **Try-lock with backoff:** Non-blocking lock attempt, retry with random delay
5. **Single-writer design:** Avoid distributed locks entirely (partition by key)

---

### Q14: What is the Outbox pattern and why is it needed?

**Problem:** A service needs to atomically update its database AND publish an event. These are two separate systems — a crash between them causes inconsistency.

**Solution:** Write the event to an "outbox" table in the **same database transaction** as the business data. A separate process reads the outbox and publishes to the message broker.

**Implementation:** CDC tools like Debezium can tail the database log and automatically publish outbox events.

---

### Q15: Explain vector clocks and how they detect concurrent writes.

Each node maintains a vector of counters (one per node). On each event, increment own counter. On receive, take element-wise max + increment own counter.

**Comparing vectors:**
- `[3,1,0]` vs `[2,2,0]` → Neither dominates → **CONCURRENT** (conflict!)
- `[3,1,0]` vs `[2,0,0]` → First dominates → **Causal ordering** (no conflict)

Used by DynamoDB and Riak to detect concurrent writes and let the application resolve conflicts.

---

### Q16: How would you design a multi-region distributed system?

```
Key decisions:
1. Active-Active vs Active-Passive
   - Active-Active: both regions serve traffic (lower latency, conflict risk)
   - Active-Passive: one region primary, other for DR (simpler, higher RTO)

2. Data replication:
   - Synchronous: strong consistency, higher latency (~100ms cross-region)
   - Asynchronous: eventual consistency, low latency

3. Conflict resolution:
   - LWW (Last-Writer-Wins) for most data
   - CRDTs for counters, sets
   - Application-level merge for complex cases

4. Traffic routing:
   - GeoDNS or Global Load Balancer → route to nearest region
   - Failover: DNS health checks → redirect on failure

5. Data residency:
   - Keep EU data in EU, US data in US (GDPR)
   - Zone sharding (MongoDB zones, CockroachDB localities)
```

---

## ⚡ Rapid-Fire Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | What does CAP stand for? | Consistency, Availability, Partition Tolerance |
| 2 | What is a partition in CAP? | Network failure splitting nodes into groups that can't communicate |
| 3 | Raft or Paxos — which is used more in practice? | Raft (etcd, CockroachDB, Consul, TiKV) |
| 4 | What is quorum for 5 nodes? | 3 (majority = ⌊N/2⌋ + 1) |
| 5 | What is read repair? | Client detects stale replica on read and sends it the latest value |
| 6 | What are Lamport timestamps missing? | Cannot detect concurrent events (only partial ordering) |
| 7 | 2PC's main weakness? | Blocking — if coordinator crashes, participants are stuck |
| 8 | What is a tombstone? | Marker indicating a deleted record (used in leaderless/LSM systems) |
| 9 | What is back-pressure? | Pushing back on producers when consumers can't keep up |
| 10 | What is split brain? | Multiple nodes believe they are the leader simultaneously |
| 11 | CRDT stands for? | Conflict-free Replicated Data Type |
| 12 | What prevents split brain? | Quorum-based election (need majority to become leader) |
| 13 | What is a fencing token? | Monotonically increasing token to invalidate stale leaders |
| 14 | MTTR vs MTTF? | Mean Time To Repair vs Mean Time To Failure |
| 15 | What is the FLP impossibility result? | Consensus is impossible in purely async systems with even 1 crash |
| 16 | What is a lease? | A time-limited lock (auto-expires if holder crashes) |
| 17 | What is gossip protocol? | Peer-to-peer protocol where nodes share state (like spreading rumors) |
| 18 | Write amplification? | Extra writes needed beyond the logical write (compaction, replication) |
| 19 | What is tail latency? | Latency at high percentiles (P99, P99.9) — worst-case experience |
| 20 | What is hedged requests? | Send same request to multiple replicas, use first response |

---

## 🏗️ System Design Scenarios

### Scenario 1: Design a URL Shortener (100M URLs)

```
Key decisions:
  Partitioning: Hash short-code → partition (even distribution)
  Storage: Key-value store (DynamoDB, Redis + persistence)
  ID generation: Base62 encoding of auto-incrementing ID or hash
  
  Read path: short_code → cache (Redis) → DB → redirect (301/302)
  Write path: long_url → generate short_code → store → return

  Scale:
    - 100:1 read-to-write ratio → cache-heavy
    - Redis cache for hot URLs (LRU eviction)
    - CDN at edge for popular URLs
    - Consistent hashing for cache layer
```

### Scenario 2: Design a Distributed Task Queue

```
Requirements: Exactly-once processing, retries, priority, delayed tasks

Architecture:
  Producer → Kafka (partitioned by task type) → Consumer Groups

  Guarantees:
    - At-least-once delivery (consumer commits offset AFTER processing)
    - Idempotency keys for exactly-once effect
    - DLQ (Dead Letter Queue) for failed tasks after max retries

  Priority: Separate topics for high/medium/low priority
  Delayed: Delayed message implementation or separate scheduled queue
  Monitoring: Consumer lag, processing rate, error rate
```

### Scenario 3: Design a Distributed Rate Limiter

```
Requirements: 1000 req/s per user, distributed across 10 servers

Options:
  1. Centralized (Redis):
     Each server checks Redis → INCR user:{id}:{window}
     ✅ Accurate, ❌ Redis is SPOF, latency

  2. Local + Sync:
     Each server allows 100 req/s locally (1000/10)
     Periodic sync to adjust
     ✅ Low latency, ❌ Inaccurate during sync gaps

  3. Sliding Window (Redis):
     ZADD user:{id}:requests {timestamp} {request_id}
     ZRANGEBYSCORE to count requests in window
     ZREMRANGEBYSCORE to clean old entries
     ✅ Smooth, ❌ Higher Redis memory
```
