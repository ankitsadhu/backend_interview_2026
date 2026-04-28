# Distributed Systems Study Guide

> Comprehensive distributed systems learning path from fundamentals to advanced, organized for interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | What is a distributed system, fallacies, CAP theorem, PACELC, system models, failure modes, clocks & time | 🟢 Beginner |
| 02 | [Communication](./02_communication.md) | RPC, REST vs gRPC, message queues, pub/sub, async vs sync, protocols (HTTP/2, WebSocket), serialization (Protobuf, Avro) | 🟢🟡 Beginner-Intermediate |
| 03 | [Consistency & Consensus](./03_consistency_and_consensus.md) | Strong/eventual/causal consistency, linearizability, Paxos, Raft, 2PC, 3PC, leader election, quorum | 🟡 Intermediate |
| 04 | [Replication](./04_replication.md) | Single-leader, multi-leader, leaderless replication, conflict resolution (CRDTs, LWW), chain replication | 🟡 Intermediate |
| 05 | [Partitioning & Sharding](./05_partitioning.md) | Hash vs range partitioning, consistent hashing, rebalancing, secondary indexes, hot spots | 🟡🔴 Intermediate-Advanced |
| 06 | [Distributed Storage](./06_distributed_storage.md) | LSM trees, SSTables, B-Trees, distributed file systems (HDFS, GFS), object storage, distributed databases (Cassandra, DynamoDB, CockroachDB) | 🟡🔴 Intermediate-Advanced |
| 07 | [Distributed Patterns](./07_distributed_patterns.md) | Saga, CQRS, Event Sourcing, Circuit Breaker, Sidecar, Service Mesh, Outbox, Idempotency, Bulkhead | 🔴 Advanced |
| 08 | [Scalability & Load Balancing](./08_scalability.md) | Horizontal vs vertical scaling, load balancing algorithms, CDN, caching strategies, auto-scaling, back-pressure | 🔴 Advanced |
| 09 | [Observability & Reliability](./09_observability_and_reliability.md) | Distributed tracing, logging, metrics, SLIs/SLOs/SLAs, chaos engineering, failure injection, blast radius | 🔴 Advanced |
| 10 | [Interview Questions](./10_interview_questions.md) | 25+ categorized questions (beginner → advanced) + rapid-fire Q&A + system design scenarios | 🟢🟡🔴 All Levels |

## 🎯 Study Path

### Week 1: Foundations
1. Read `01_fundamentals.md` — understand why distributed systems are hard
2. Read `02_communication.md` — how services talk to each other
3. Read `03_consistency_and_consensus.md` — the core trade-offs

### Week 2: Data Layer
4. Read `04_replication.md` — how data is copied across nodes
5. Read `05_partitioning.md` — how data is split across nodes
6. Read `06_distributed_storage.md` — storage engines and distributed databases

### Week 3: Patterns & Production
7. Read `07_distributed_patterns.md` — essential design patterns
8. Read `08_scalability.md` — scaling strategies and load balancing
9. Read `09_observability_and_reliability.md` — monitoring and resilience

### Final Review
10. Go through `10_interview_questions.md` — test yourself across all levels

## 📚 Recommended Reading

- *Designing Data-Intensive Applications* — Martin Kleppmann
- *Distributed Systems* — Maarten van Steen & Andrew Tanenbaum
- *Understanding Distributed Systems* — Roberto Vitillo
