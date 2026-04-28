# Sharding in MongoDB

## What is Sharding?

**Sharding** is MongoDB's strategy for **horizontal scaling** — distributing data across multiple machines (shards) to handle large datasets and high throughput.

```
                    Application
                        │
                        ▼
                  ┌──────────┐
                  │  mongos   │  ← Query Router
                  │  (Router) │     Routes queries to correct shard(s)
                  └─────┬────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  Shard 1  │  │  Shard 2  │  │  Shard 3  │
    │(Replica   │  │(Replica   │  │(Replica   │
    │  Set)     │  │  Set)     │  │  Set)     │
    │           │  │           │  │           │
    │ A-H data  │  │ I-P data  │  │ Q-Z data  │
    └──────────┘  └──────────┘  └──────────┘
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                  ┌──────────┐
                  │  Config   │  ← Config Servers
                  │  Servers  │    (metadata + chunk mappings)
                  │(Replica   │
                  │  Set)     │
                  └──────────┘
```

### Components

| Component | Role |
|-----------|------|
| **Shard** | Each shard is a replica set holding a subset of data |
| **mongos** | Query router — directs operations to the correct shard(s) |
| **Config Servers** | Replica set storing metadata: chunk ranges, shard mappings |
| **Chunk** | Contiguous range of shard key values (default: 128 MB) |
| **Balancer** | Background process that distributes chunks evenly across shards |

---

## Shard Keys

The **shard key** determines how data is distributed across shards. It is the **most critical decision** in sharding.

```javascript
// Shard a collection
sh.enableSharding("mydb")
sh.shardCollection("mydb.orders", { customer_id: 1 })     // Ranged
sh.shardCollection("mydb.events", { event_id: "hashed" })  // Hashed
```

### Ranged Sharding

Documents are distributed based on **shard key value ranges**.

```
Shard Key: { age: 1 }

Chunk 1 (Shard A): age [0, 20)
Chunk 2 (Shard B): age [20, 40)
Chunk 3 (Shard C): age [40, 60)
Chunk 4 (Shard A): age [60, ∞)
```

**Pros:** Efficient range queries on shard key
**Cons:** Uneven distribution if values are monotonically increasing (e.g., timestamps)

### Hashed Sharding

Shard key value is **hashed** before distribution → even spread.

```
Shard Key: { _id: "hashed" }

hash(ObjectId("aaa")) → 0x2F... → Shard B
hash(ObjectId("aab")) → 0x8C... → Shard C
hash(ObjectId("aac")) → 0x1A... → Shard A
// Even distribution, regardless of input pattern
```

**Pros:** Even data distribution, no hot spots
**Cons:** Range queries become scatter-gather (must hit all shards)

### Choosing a Good Shard Key

| Criterion | Good Shard Key | Bad Shard Key |
|-----------|---------------|---------------|
| **High cardinality** | `user_id` (millions of values) | `status` (3 values: active/inactive/pending) |
| **Even distribution** | `hashed(_id)`, `compound(region, ts)` | `created_at` (monotonic — all writes to one shard) |
| **Query isolation** | Field used in most queries | Field rarely in queries (scatter-gather) |
| **Non-monotonic** | UUID, hashed field | Auto-incrementing ID, timestamp |
| **Immutable** | `user_id` | `email` (might change) |

### Compound Shard Keys

```javascript
// Compound shard key — best of both worlds
sh.shardCollection("mydb.orders", { region: 1, order_date: 1 })

// - region: provides query isolation (targeted queries)
// - order_date: provides range queries within a region
// - Together: good distribution + efficient queries
```

---

## How Queries Route in Sharded Clusters

### Targeted Query (Best Performance)

Query includes the **shard key** → mongos routes to specific shard(s).

```javascript
// Shard key: { customer_id: 1 }
db.orders.find({ customer_id: "alice" })  // → Shard B only
// Time: O(log n) on one shard
```

### Scatter-Gather Query (Worst Performance)

Query does **NOT include shard key** → mongos broadcasts to ALL shards.

```javascript
// Shard key: { customer_id: 1 }
db.orders.find({ status: "shipped" })  // → ALL shards
// Each shard runs query → mongos merges results
// Time: O(n) across all shards
```

### Query Routing Summary

| Query Pattern | Routing | Performance |
|--------------|---------|-------------|
| Filter on shard key (exact) | **Targeted** → 1 shard | 🟢 Best |
| Filter on shard key (range) | **Targeted** → subset of shards | 🟡 Good |
| Filter on compound shard key prefix | **Targeted** → subset | 🟡 Good |
| No shard key in filter | **Scatter-gather** → ALL shards | 🔴 Worst |
| Sort on shard key | **Distributed merge sort** | 🟡 Moderate |

---

## Chunks and the Balancer

### Chunks

A **chunk** is a contiguous range of shard key values assigned to a shard.

```
Collection: orders, Shard Key: { customer_id: 1 }

Chunk 1: [MinKey, "customer_500")   → Shard A
Chunk 2: ["customer_500", "customer_1000") → Shard B
Chunk 3: ["customer_1000", MaxKey) → Shard C
```

**Default chunk size:** 128 MB (configurable: 1 MB – 1024 MB)

### Chunk Splitting

When a chunk exceeds `chunkSize`, it splits automatically:

```
Before split:
  Chunk 1: [MinKey, "customer_1000") → 200 MB (too large!)

After split:
  Chunk 1a: [MinKey, "customer_500")     → 100 MB
  Chunk 1b: ["customer_500", "customer_1000") → 100 MB
```

### The Balancer

Background process that **migrates chunks** to maintain even distribution.

```javascript
// Balancer status
sh.getBalancerState()
sh.isBalancerRunning()

// Enable/disable balancer
sh.enableBalancing("mydb.orders")
sh.disableBalancing("mydb.orders")

// Set balancer window (run only during off-peak hours)
db.settings.updateOne(
  { _id: "balancer" },
  {
    $set: {
      activeWindow: { start: "02:00", stop: "06:00" }
    }
  },
  { upsert: true }
)
```

### Jumbo Chunks

A **jumbo chunk** is a chunk that exceeds `chunkSize` but **cannot be split** (all documents have the same shard key value).

```
Example: Shard key { status: 1 }
  Chunk: [status: "active", status: "active") → has 500K documents!
  Cannot split because all have the same shard key value!
  → Jumbo chunk → causes imbalance
```

**Prevention:** Choose shard keys with **high cardinality**.

---

## Zone Sharding

Assign **ranges of shard key values** to specific shards (geographic data locality).

```javascript
// Tag shards with zones
sh.addShardTag("shard-us-east", "US")
sh.addShardTag("shard-eu-west", "EU")
sh.addShardTag("shard-ap-south", "APAC")

// Define zone ranges
sh.addTagRange(
  "mydb.users",
  { region: "US", _id: MinKey },
  { region: "US", _id: MaxKey },
  "US"
)
sh.addTagRange(
  "mydb.users",
  { region: "EU", _id: MinKey },
  { region: "EU", _id: MaxKey },
  "EU"
)

// Now: US users → US shard, EU users → EU shard
// Achieves data residency requirements (GDPR) and lower latency
```

---

## Resharding (MongoDB 5.0+)

Change the shard key of an existing sharded collection **without downtime**.

```javascript
// Reshard collection with new key
db.adminCommand({
  reshardCollection: "mydb.orders",
  key: { customer_id: 1, order_date: 1 }  // New shard key
})

// Process:
// 1. Creates new shard key index
// 2. Copies all data using new key distribution
// 3. Switches over atomically
// 4. Drops old chunks

// ⚠️ Resource-intensive — increases disk usage during resharding
```

---

## Sharding Admin Commands

```javascript
// Enable sharding on database
sh.enableSharding("mydb")

// Shard a collection
sh.shardCollection("mydb.orders", { order_id: "hashed" })

// Check sharding status
sh.status()

// Check chunk distribution
db.orders.getShardDistribution()

// Move chunk to specific shard
sh.moveChunk("mydb.orders", { order_id: "some_value" }, "shard3")

// Split chunk at specific point
sh.splitAt("mydb.orders", { order_id: "midpoint" })
sh.splitFind("mydb.orders", { order_id: "find_chunk" })

// Add a shard
sh.addShard("shard4/mongo4a:27017,mongo4b:27017,mongo4c:27017")

// Remove a shard (drains data first)
db.adminCommand({ removeShard: "shard4" })

// Check shard status during removal
db.adminCommand({ removeShard: "shard4" })  // Call again to check progress
```

---

## When to Shard

### Shard When:

| Signal | Explanation |
|--------|-------------|
| **Working set > RAM** | Data no longer fits in memory, performance degrades |
| **Write throughput** | Single primary can't handle write load |
| **Storage capacity** | Single server can't store all data |
| **Geographic distribution** | Data must be near users (via zones) |
| **Compliance** | Data residency requirements (GDPR) |

### Don't Shard When:

| Signal | Explanation |
|--------|-------------|
| **Small dataset** | Sharding adds complexity with no benefit |
| **Can scale vertically** | Bigger server is simpler |
| **Read-heavy only** | Use replica set with secondary reads |
| **No clear shard key** | Bad shard key = worse performance than no sharding |

---

## Sharding Best Practices

### 1. Choose the Right Shard Key First Time

```
The shard key is (practically) permanent:
- Pre-5.0: CANNOT change shard key after creation
- 5.0+: Can reshard, but it's expensive

Bad shard key = years of performance problems
```

### 2. Avoid Monotonic Shard Keys

```javascript
// ❌ BAD — all writes go to one shard (hot shard)
sh.shardCollection("mydb.logs", { timestamp: 1 })

// ✅ GOOD — hashed for even distribution
sh.shardCollection("mydb.logs", { _id: "hashed" })

// ✅ GOOD — compound with leading non-monotonic field
sh.shardCollection("mydb.logs", { service: 1, timestamp: 1 })
```

### 3. Include Shard Key in Frequent Queries

```javascript
// Shard key in query = targeted (fast)
db.orders.find({ customer_id: "alice" })

// Shard key NOT in query = scatter-gather (slow)
db.orders.find({ status: "shipped" })
```

### 4. Plan for Data Growth

```
Start with 3 shards minimum
Add shards as needed — the balancer redistributes chunks automatically
Each shard should be a 3-member replica set
```

---

## Interview Questions — Sharding

### Q1: What is the difference between ranged and hashed sharding?

| Aspect | Ranged | Hashed |
|--------|--------|--------|
| Distribution | Based on value ranges | Based on hash of value |
| Range queries | Targeted (efficient) | Scatter-gather (all shards) |
| Data distribution | Can be uneven (hot spots) | Even distribution |
| Write distribution | Uneven for sequential keys | Even |
| Use case | Natural ranges (time, geography) | Even distribution priority |

### Q2: What makes a bad shard key?

1. **Low cardinality** — few distinct values → jumbo chunks
2. **Monotonically increasing** — all writes to last chunk (hot shard)
3. **Rarely used in queries** — causes scatter-gather queries
4. **Mutable** — shard key is immutable after insert
5. **Examples of bad keys:** `{ status: 1 }`, `{ created_at: 1 }`, `{ boolean_flag: 1 }`

### Q3: How does the balancer work?

1. Runs as a background process on one `mongos` (the "balancer coordinator")
2. Monitors chunk distribution across shards
3. When imbalance exceeds threshold (default: 2 chunks difference), migrates chunks
4. During migration: source shard → copies chunk data → destination shard → updates config servers
5. Configurable: can set active windows, disable for maintenance
6. **Does NOT rebalance indexes** — each shard maintains its own indexes

### Q4: What happens when you add a new shard to a cluster?

1. New shard registers with config servers (via `sh.addShard()`)
2. Balancer detects imbalance (new shard has 0 chunks)
3. Balancer migrates chunks from overloaded shards to new shard
4. Process is gradual — no downtime, but increased network I/O
5. Eventually, data is evenly distributed across all shards

### Q5: Can you change a shard key after sharding a collection?

- **Before MongoDB 5.0:** No — shard key is permanent (must recreate collection)
- **MongoDB 5.0+:** Yes — use `reshardCollection` command (no downtime, but resource-intensive)
- **MongoDB 5.0+:** Can also **refine** shard key by adding suffix fields
  ```javascript
  db.adminCommand({
    refineCollectionShardKey: "mydb.orders",
    key: { customer_id: 1, order_id: 1 }  // Added order_id
  })
  ```
