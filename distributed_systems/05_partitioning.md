# Partitioning & Sharding

## Why Partition Data?

When data or query load exceeds what a single node can handle, **partition** (shard) the data across multiple nodes.

```
Single Node (limits):                Multiple Partitions:
┌───────────────────┐               ┌────────┐ ┌────────┐ ┌────────┐
│  ALL data (100TB) │   ────→       │ Node A │ │ Node B │ │ Node C │
│  ALL queries      │               │  33TB  │ │  33TB  │ │  33TB  │
│  CPU saturated    │               │ 1/3    │ │ 1/3    │ │ 1/3    │
└───────────────────┘               │ queries│ │ queries│ │ queries│
                                    └────────┘ └────────┘ └────────┘
```

| Goal | How Partitioning Helps |
|------|----------------------|
| **Storage** | Spread data across multiple disks/machines |
| **Throughput** | Parallelize queries across partitions |
| **Latency** | Smaller dataset per node → faster queries |
| **Availability** | Partition failure doesn't lose ALL data |

---

## Partitioning Strategies

### 1. Range Partitioning

Assign contiguous ranges of the key space to each partition.

```
Key: user_id (alphabetical)

Partition 1: A–F  →  Node A
Partition 2: G–M  →  Node B
Partition 3: N–S  →  Node C
Partition 4: T–Z  →  Node D

Query: "Find users with names starting with A-C"
  → Only hits Partition 1 (targeted, efficient!)
```

**Pros:** Efficient range queries, natural ordering
**Cons:** **Hot spots** if data is skewed (e.g., most users start with "S")

### 2. Hash Partitioning

Hash the key → distribute evenly across partitions.

```
Key: user_id
Partition = hash(user_id) % num_partitions

hash("alice") = 0x3F... → Partition 2
hash("bob")   = 0xA1... → Partition 0
hash("carol") = 0x72... → Partition 3

Distribution is uniform regardless of key patterns.
```

**Pros:** Even distribution, no hot spots from sequential keys
**Cons:** Range queries become scatter-gather (must query ALL partitions)

### 3. Compound Partitioning (Hybrid)

First part of key → determines partition (range). Remaining → sorts within partition.

```
Compound key: (user_id, timestamp)

Partition by: hash(user_id)
Sort within partition by: timestamp

Query: "Get all posts by user_id='alice' between Jan-Mar"
  → Hash(alice) → Partition 2 → range scan on timestamp
  → Targeted AND efficient!
```

Used by: Cassandra (partition key + clustering key), DynamoDB (partition key + sort key)

---

## Consistent Hashing

Standard hash partitioning (`hash(key) % N`) breaks when N changes (adding/removing nodes). Consistent hashing minimizes data movement.

```
Traditional:                    Consistent Hashing:
hash(key) % 3                  Place nodes on a hash ring
  Node 0: keys 0,3,6...         Only keys in the affected 
  Node 1: keys 1,4,7...         arc move when a node is
  Node 2: keys 2,5,8...         added/removed

Add Node 3:                    Add Node D:
hash(key) % 4                  Only keys between C and D
  ALL keys redistributed!      are moved to D (~1/N keys)
  ❌ Massive data movement      ✅ Minimal data movement

Hash Ring:
          0°
          │
    ┌─────●─────┐         ● = Node
    │  Node A   │         Each key hashes to a
  270°          90°        position on the ring,
    │  Node C   │         assigned to the next
    └─────●─────┘         node clockwise
         180°
       Node B
```

### Virtual Nodes (vnodes)

**Problem:** With few physical nodes, distribution is uneven.
**Solution:** Each physical node gets multiple positions on the ring.

```
Instead of 3 nodes on the ring:
  A, B, C

Use virtual nodes (e.g., 256 per physical node):
  A1, A2, ... A256, B1, B2, ... B256, C1, C2, ... C256

Benefits:
  - More uniform distribution
  - When node fails, its load spreads across ALL other nodes (not just one)
  - Easy to handle heterogeneous hardware (powerful node = more vnodes)
```

Used by: DynamoDB, Cassandra, Riak, Memcached

---

## Rebalancing

Moving data between partitions when nodes are added, removed, or data grows unevenly.

### Strategies

| Strategy | Description | Pros | Cons |
|----------|-------------|------|------|
| **Fixed partitions** | Create many partitions upfront (e.g., 1000). Assign multiple to each node. | Simple, predictable | Must guess partition count |
| **Dynamic splitting** | Split partition when it grows too large | Adapts to data | Complex, may cause cascading splits |
| **Proportional** | Number of partitions proportional to number of nodes | Even load | Requires data movement |

```
Fixed Partitions (most common):
  Start: 1000 partitions on 3 nodes
    Node A: partitions 0-333
    Node B: partitions 334-666
    Node C: partitions 667-999

  Add Node D:
    Node A: partitions 0-249
    Node B: partitions 250-499
    Node C: partitions 500-749
    Node D: partitions 750-999
    
    Only ~25% of partitions moved (to new node)
```

### Automatic vs Manual Rebalancing

| Approach | Example | Trade-off |
|----------|---------|-----------|
| **Fully automatic** | Cassandra, DynamoDB | Convenient but risky (cascading failure) |
| **Semi-automatic** | MongoDB (balancer) | System suggests, admin approves |
| **Manual** | HBase | Full control, requires expertise |

---

## Hot Spots

When some partitions receive disproportionately more traffic than others.

```
Celebrity Problem:
  Justin Bieber posts → millions of reads for that post
  All go to ONE partition → that node is overwhelmed

Causes:
  1. Skewed data distribution (some keys much more popular)
  2. Temporal patterns (all today's data on one partition)
  3. Bad partition key (low cardinality)
```

### Mitigation Strategies

```
1. Add random prefix/suffix to hot keys
   key = "user_123" → "user_123_" + random(0-9)
   Spreads across 10 partitions
   Trade-off: reads must query all 10 and merge

2. Dedicated partitions for hot keys
   Route "celebrity_user" to a dedicated, scaled partition

3. Read replicas for hot partitions
   Replicate the hot partition to more nodes for reads

4. Caching
   Cache hot data in front of the partition (Redis, Memcached)
   Most effective for read-heavy hot spots
```

---

## Secondary Indexes in Partitioned Systems

Querying by non-partition-key fields requires secondary indexes.

### Local Index (Document-Based Partitioning)

Each partition maintains its **own** secondary index covering only its data.

```
Partition 0:                    Partition 1:
  Data: cars {color: red}        Data: cars {color: red}
             {color: blue}                  {color: red}
  
  Local index:                   Local index:
    red → [doc1]                   red → [doc3, doc4]
    blue → [doc2]                  

Query: "Find all red cars"
  → Must query ALL partitions (scatter-gather)
  → Each partition searches its local index
  → Merge results
```

**Pros:** Writes are fast (update only local index)
**Cons:** Reads by secondary key must fan-out to all partitions

### Global Index (Term-Based Partitioning)

A single index covering all partitions, itself partitioned.

```
Partition 0 (data):             Partition 1 (data):
  cars {color: red}               cars {color: red}
       {color: blue}                   {color: green}

Global Index (by first letter of color):
  Index Partition A (a-m):        Index Partition B (n-z):
    blue → [P0:doc2]               red → [P0:doc1, P1:doc3]
    green → [P1:doc4]              

Query: "Find all red cars"
  → Go to Index Partition B (where "red" lives)
  → Get [P0:doc1, P1:doc3]
  → Fetch from data partitions
  → Single index lookup! (no scatter-gather)
```

**Pros:** Fast reads (targeted index lookup)
**Cons:** Writes slower (must update index on a different partition, async)

Used by: DynamoDB (Global Secondary Indexes), Elasticsearch (each index is a set of shards)

---

## Partitioning + Replication

In practice, **each partition is replicated** for fault tolerance.

```
Partition 1:            Partition 2:            Partition 3:
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ Node A       │       │ Node B       │       │ Node C       │
│ (Leader P1)  │       │ (Leader P2)  │       │ (Leader P3)  │
│ (Follower P2)│       │ (Follower P3)│       │ (Follower P1)│
│ (Follower P3)│       │ (Follower P1)│       │ (Follower P2)│
└──────────────┘       └──────────────┘       └──────────────┘

Each node holds:
  - Leader for 1 partition (accepts writes)
  - Follower for 2 other partitions (replication)
```

---

## Interview Questions — Partitioning

### Q1: What is the difference between partitioning and replication?

| Aspect | Partitioning | Replication |
|--------|-------------|-------------|
| Purpose | Split data across nodes | Copy data across nodes |
| Each node holds | Subset of data | Full copy of data |
| Solves | Scalability (storage + throughput) | Availability + read performance |
| Used together? | Yes! Each partition is typically replicated |

### Q2: Why is consistent hashing better than `hash(key) % N`?

With `hash(key) % N`, adding a node changes N → almost all keys remap → massive data movement.
With consistent hashing, only `~1/N` of keys move to the new node. Virtual nodes further improve balance.

### Q3: How does DynamoDB handle partitioning?

1. **Partition key** determines which partition stores the item (consistent hashing)
2. **Sort key** (optional) determines ordering within a partition
3. **GSIs** (Global Secondary Indexes) → term-based partitioning of secondary indexes
4. **Automatic splitting** when partition grows too large or gets too hot
5. **Adaptive capacity** → redistributes throughput from underused to hot partitions

### Q4: How would you design a partition key for a time-series database?

```
❌ BAD: partition by timestamp
  → All writes go to "current" partition → hot spot!

✅ GOOD: partition by (sensor_id, time_bucket)
  → Spreads writes across sensors
  → Can still range-query within a sensor
  
  Example: sensor_id = "temp_01", time_bucket = "2026-03-17"
  → Partition key = "temp_01#2026-03-17"
```
