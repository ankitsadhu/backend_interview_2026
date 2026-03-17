# MongoDB Interview Questions

> Comprehensive question bank covering beginner to advanced topics, rapid-fire, and system design.

---

## 🟢 Beginner Level

### Q1: What is MongoDB and how does it differ from SQL databases?

MongoDB is a **document-oriented NoSQL database** that stores data as flexible BSON documents instead of fixed-schema rows in tables.

| Aspect | SQL (e.g., PostgreSQL) | MongoDB |
|--------|----------------------|---------|
| Data Model | Tables with rows & columns | Collections with documents |
| Schema | Fixed schema (DDL) | Flexible schema (schema-less) |
| Relationships | JOINs (normalized) | Embedding or referencing |
| Scaling | Primarily vertical | Horizontal (sharding built-in) |
| Transactions | Full ACID (always) | ACID for single-doc (always), multi-doc (4.0+) |
| Query Language | SQL | MongoDB Query Language (MQL) |
| Best For | Complex relationships, strict consistency | Hierarchical data, rapid iteration, scale |

---

### Q2: Explain the MongoDB document model.

```javascript
// A document is a JSON-like structure (stored as BSON)
{
  _id: ObjectId("507f1f77bcf86cd799439011"),  // Primary key (auto-generated)
  name: "Alice",                              // String field
  age: 30,                                    // Number field
  tags: ["developer", "admin"],               // Array field
  address: {                                  // Embedded document
    city: "NYC",
    zip: "10001"
  },
  createdAt: ISODate("2026-03-17")            // Date field
}
```

**Key properties:**
- Max document size: **16 MB**
- `_id` is auto-generated (ObjectId) if not provided
- Documents in the same collection can have different fields
- Rich types: ObjectId, Date, Decimal128, Binary, etc.

---

### Q3: What is an ObjectId? How is it structured?

```
12 bytes total:
┌──────────┬──────────────┬──────────┐
│ 4 bytes  │   5 bytes    │ 3 bytes  │
│timestamp │   random     │ counter  │
└──────────┴──────────────┴──────────┘
```

- **Time-sortable** (first 4 bytes = Unix timestamp)
- **Unique** across machines without coordination
- Extract timestamp: `ObjectId("...").getTimestamp()`

---

### Q4: What is the difference between `find()` and `findOne()`?

| Method | Returns | Use Case |
|--------|---------|----------|
| `find()` | **Cursor** (lazy iterator over all matches) | Multiple documents |
| `findOne()` | **Single document** (first match) or `null` | One document by _id or unique field |

```javascript
db.users.find({ age: { $gt: 25 } })     // Returns cursor
db.users.findOne({ _id: ObjectId("...") })  // Returns document
```

---

### Q5: What is the difference between `deleteMany({})` and `drop()`?

| Operation | Action | Indexes | Speed |
|-----------|--------|---------|-------|
| `deleteMany({})` | Removes all documents | **Keeps** indexes | Slow (per-document) |
| `drop()` | Removes entire collection | **Drops** indexes | Instant |

---

### Q6: How does MongoDB handle schema validation?

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "email"],
      properties: {
        name: { bsonType: "string" },
        email: { bsonType: "string", pattern: "^.+@.+$" }
      }
    }
  },
  validationLevel: "strict",   // "strict" | "moderate"
  validationAction: "error"    // "error" | "warn"
})
```

---

## 🟡 Intermediate Level

### Q7: Explain embedding vs referencing with trade-offs.

**Embed when:** Data is always accessed together, bounded size, one-to-few relationship.
**Reference when:** Data is accessed independently, unbounded growth, many-to-many.

| Factor | Embed ✅ | Reference ✅ |
|--------|---------|-------------|
| Read performance | Faster (one read) | Slower ($lookup needed) |
| Write performance | Slower (larger doc) | Faster (smaller docs) |
| Atomicity | Single-doc atomic | Need transactions |
| Data duplication | Possible | Avoided |
| Document size | Risk 16 MB limit | No limit concern |

---

### Q8: What is a covered query?

A query where **all fields come from the index** — MongoDB doesn't need to read documents.

```javascript
db.users.createIndex({ email: 1, name: 1 })

// Covered — returns only indexed fields
db.users.find({ email: "alice@example.com" }, { email: 1, name: 1, _id: 0 })
// explain(): totalDocsExamined = 0 ← no document reads!
```

**Requirements:** Query filter + projection + sort all satisfied by the index. Must exclude `_id` (unless it's in the index).

---

### Q9: Explain the aggregation pipeline with an example.

```javascript
// Monthly revenue report
db.orders.aggregate([
  { $match: { status: "completed" } },                    // Filter
  { $group: {                                              // Group
      _id: { $month: "$created_at" },
      revenue: { $sum: "$total" },
      orders: { $sum: 1 }
  }},
  { $sort: { "_id": 1 } },                                // Sort by month
  { $project: { month: "$_id", revenue: 1, orders: 1, _id: 0 } }
])
```

**Key principle:** Each stage transforms data and passes it to the next. Place `$match` and `$project` early for performance.

---

### Q10: What are read concerns and why do they matter?

| Level | Guarantee | Use Case |
|-------|-----------|----------|
| `local` | Latest data from this node (may be rolled back) | General purpose |
| `majority` | Data ack'd by majority (durable) | Financial data |
| `linearizable` | Data reflects all prior writes | Critical reads |
| `snapshot` | Transaction-time consistent snapshot | Multi-doc transactions |

---

### Q11: Explain the difference between `$push`, `$addToSet`, and `$pull`.

```javascript
{ $push: { tags: "new" } }        // Always appends (allows duplicates)
{ $addToSet: { tags: "new" } }    // Appends ONLY if not already present
{ $pull: { tags: "remove_me" } }  // Removes all matching elements
```

---

### Q12: What is an explain plan and what should you look for?

```javascript
db.users.find({ email: "alice@example.com" }).explain("executionStats")
```

**Key metrics:**

| Metric | Good | Bad |
|--------|------|-----|
| `stage` | `IXSCAN` | `COLLSCAN` |
| `totalKeysExamined / nReturned` | ≈ 1 | >> 1 |
| `totalDocsExamined / nReturned` | ≈ 1 (0 = covered) | >> 1 |
| In-memory `SORT` stage | Absent | Present (needs index) |

---

## 🟡🔴 Intermediate-Advanced Level

### Q13: How does a MongoDB replica set handle failover?

1. Primary fails → heartbeat timeout (10 seconds)
2. Secondaries detect failure
3. Eligible member (highest priority + most recent data) calls election
4. Majority vote required (Raft-like protocol)
5. Winner becomes new primary (~10-12 seconds total)
6. Drivers auto-detect new primary
7. Old primary rejoins as secondary (may rollback unreplicated writes)

**Prevent rollbacks:** Use `w: "majority"` write concern.

---

### Q14: What is the oplog and why is its size important?

The **oplog** (operations log) is a capped collection on the primary that records all write operations. Secondaries replicate by tailing it.

**Oplog window** = how far back the oplog goes. If a secondary falls behind more than the oplog window → needs **full resync** (copies entire dataset).

```javascript
rs.printReplicationInfo()
// Shows oplog size and time window
```

**Sizing:** Larger oplog = more time for secondaries to catch up after maintenance/outages.

---

### Q15: Explain ranged vs hashed sharding.

| Aspect | Ranged | Hashed |
|--------|--------|--------|
| Distribution | By value ranges | By hash of value |
| Range queries | Targeted (1 shard) | Scatter-gather (all shards) |
| Write distribution | Uneven for sequential keys | Even |
| Best for | Natural ranges (time, geo) | Even distribution |

**Common mistake:** Using `{ created_at: 1 }` as ranged shard key → all writes go to one shard (hot spot).

---

### Q16: What are the ACID properties in MongoDB transactions?

Since MongoDB 4.0 (replica sets) / 4.2 (sharded clusters):

- **Atomicity** — All operations commit or none do
- **Consistency** — Validation rules enforced
- **Isolation** — Snapshot isolation within transaction
- **Durability** — With `w: "majority", j: true`

```javascript
const session = client.startSession();
session.startTransaction();
try {
  await db.accounts.updateOne({ _id: "alice" }, { $inc: { balance: -100 } }, { session });
  await db.accounts.updateOne({ _id: "bob" }, { $inc: { balance: 100 } }, { session });
  await session.commitTransaction();
} catch (e) {
  await session.abortTransaction();
} finally {
  session.endSession();
}
```

**Best practice:** Use transactions as a last resort — good schema design (embedding) provides single-document atomicity for free.

---

### Q17: How does the WiredTiger cache work?

- **In-memory cache** for frequently accessed data + indexes
- **Default size:** 50% of (RAM - 1 GB) or 256 MB (minimum)
- Uses **MVCC** — readers don't block writers
- **Document-level locking** (not collection or database level)
- Data compressed on disk (`snappy`), uncompressed in cache
- **Eviction:** When cache is full, cold data evicted to make room

**Monitor:** If `"pages evicted by application threads"` is high → cache too small.

---

## 🔴 Advanced Level

### Q18: How does MongoDB handle write conflicts in concurrent transactions?

MongoDB uses **write conflict detection**:

1. Two transactions modify the same document
2. First to commit wins
3. Second gets `WriteConflict` error
4. Driver automatically retries (with `retryWrites: true`)
5. If retry also fails → application handles the error

```
Transaction A: read doc X (version 1) → write doc X
Transaction B: read doc X (version 1) → write doc X

If A commits first:
  → doc X is now version 2
  → B tries to commit → WriteConflict (version mismatch)
  → B retried with version 2
```

---

### Q19: How would you design a shard key for a multi-tenant SaaS application?

```javascript
// Option 1: Tenant ID (ranged) — workload isolation
sh.shardCollection("mydb.data", { tenant_id: 1 })
// ✅ Targeted queries per tenant
// ❌ Hot tenant (large customer) = hot shard

// Option 2: Tenant ID + Hashed ID (compound)
sh.shardCollection("mydb.data", { tenant_id: 1, _id: "hashed" })
// ✅ Targeted by tenant + even distribution within
// ✅ Best for most SaaS applications

// Option 3: Zone sharding (data residency)
sh.addShardTag("shard-us", "US")
sh.addTagRange("mydb.data", { tenant_id: "us_001" }, { tenant_id: "us_999" }, "US")
// ✅ GDPR compliance — EU data stays in EU
```

---

### Q20: Explain Change Streams and their use cases.

Change Streams provide a **real-time stream** of data changes. Built on the oplog.

```javascript
const stream = db.orders.watch([
  { $match: { "fullDocument.status": "critical" } }
]);

stream.on("change", (event) => {
  // event.operationType: "insert" | "update" | "delete" | "replace"
  // event.fullDocument: the document (if updateLookup)
  // event._id: resume token
});
```

**Use cases:** Real-time notifications, cache invalidation, data sync between services, ETL pipelines.
**Requirements:** Replica set or sharded cluster (NOT standalone).

---

### Q21: How does MongoDB's `$graphLookup` work?

**Recursive lookup** for graph-structured data (hierarchies, networks).

```javascript
// Employee org chart: find all reports under a manager
db.employees.aggregate([
  { $match: { _id: "ceo" } },
  {
    $graphLookup: {
      from: "employees",
      startWith: "$_id",
      connectFromField: "_id",
      connectToField: "manager_id",
      as: "allReports",
      maxDepth: 10,
      depthField: "level"
    }
  }
])
```

---

### Q22: What is the Bucket Pattern and when should you use it?

**Problem:** Time-series data creates millions of tiny documents.
**Solution:** Group data into time-based "buckets."

```javascript
// Instead of 1 doc per sensor reading...
// Group 3600 readings per hour into one document
{
  sensor_id: "temp_01",
  bucket_start: ISODate("2026-03-17T10:00:00"),
  count: 3600,
  avg: 22.5,
  readings: [{ t: ISODate("..."), v: 22.5 }, ...]
}
```

**Benefits:** 60x fewer documents, pre-aggregated stats, better cache efficiency.
**MongoDB 5.0+:** Native Time Series collections handle this automatically.

---

## ⚡ Rapid-Fire Questions

| # | Question | Answer |
|---|----------|--------|
| 1 | Max document size? | 16 MB |
| 2 | Default port? | 27017 |
| 3 | Default storage engine? | WiredTiger |
| 4 | What is BSON? | Binary JSON — binary-encoded, type-rich JSON |
| 5 | Min replica set members? | 3 (1 primary + 2 secondaries or 1 primary + 1 secondary + 1 arbiter) |
| 6 | How many text indexes per collection? | 1 |
| 7 | Can you change `_id` after insert? | No, it's immutable |
| 8 | What does `w: "majority"` do? | Write acknowledged by majority of replica set members |
| 9 | What is an arbiter? | Votes in elections but holds no data |
| 10 | Default chunk size in sharding? | 128 MB |
| 11 | Can MongoDB do JOINs? | Yes, via `$lookup` in aggregation (left outer join) |
| 12 | What is a capped collection? | Fixed-size collection, auto-deletes oldest documents |
| 13 | What is `explain()`? | Shows query execution plan (index usage, scanned docs) |
| 14 | What causes a jumbo chunk? | Low-cardinality shard key → chunk can't be split |
| 15 | What is GridFS? | File storage using two collections (files + chunks) for >16 MB |
| 16 | Difference between `$set` and `$unset`? | `$set` updates fields, `$unset` removes fields |
| 17 | What is the oplog? | Capped collection logging all write operations for replication |
| 18 | TTL index? | Auto-deletes documents after a time period |
| 19 | Can arrays be in a compound index? | Yes, but only ONE array field per compound index |
| 20 | What is `readPreference: "nearest"`? | Route reads to lowest-latency replica set member |

---

## 🏗️ System Design with MongoDB

### Design: Real-Time Chat Application

**Requirements:**
- 1:1 and group messaging
- Read receipts
- Message history
- Online status
- 10M users, 1B messages/month

**Schema Design:**

```javascript
// users collection
{
  _id: ObjectId("user1"),
  name: "Alice",
  avatar: "...",
  status: "online",
  last_seen: ISODate("2026-03-17T10:30:00Z")
}

// conversations collection (lightweight metadata)
{
  _id: ObjectId("conv1"),
  type: "group",                    // "direct" | "group"
  participants: [ObjectId("user1"), ObjectId("user2"), ObjectId("user3")],
  last_message: {                   // Subset pattern — latest message embedded
    text: "Hello everyone!",
    sender: ObjectId("user1"),
    sent_at: ISODate("2026-03-17T10:30:00Z")
  },
  unread_counts: {                  // Per-participant unread count
    "user2": 3,
    "user3": 1
  }
}

// messages collection (bulk of data)
{
  _id: ObjectId("msg1"),
  conversation_id: ObjectId("conv1"),
  sender_id: ObjectId("user1"),
  text: "Hello everyone!",
  type: "text",                    // "text" | "image" | "file"
  sent_at: ISODate("2026-03-17T10:30:00Z"),
  read_by: [
    { user_id: ObjectId("user2"), read_at: ISODate("2026-03-17T10:31:00Z") }
  ]
}
```

**Indexes:**
```javascript
db.messages.createIndex({ conversation_id: 1, sent_at: -1 })  // Message history
db.conversations.createIndex({ participants: 1 })               // User's conversations
db.users.createIndex({ status: 1, last_seen: -1 })             // Online users
```

**Scaling:**
- **Shard key:** `{ conversation_id: "hashed" }` for messages
- **Change Streams** for real-time delivery
- **TTL index** on message `read_by` for cleanup
- **Redis** for online status and typing indicators (hot data)

---

### Design: E-Commerce Product Catalog

**Requirements:**
- 10M products, 500K daily searches
- Faceted search (category, price range, brand, rating)
- Product recommendations
- Inventory tracking

```javascript
// products collection — polymorphic pattern
{
  _id: ObjectId("prod1"),
  name: "Wireless Headphones",
  slug: "wireless-headphones-pro-v2",
  category: ["electronics", "audio", "headphones"],
  brand: "AudioTech",
  price: { amount: NumberDecimal("79.99"), currency: "USD" },
  inventory: {
    total: 500,
    reserved: 23,
    available: 477
  },
  ratings: {
    avg: 4.3,
    count: 1247,
    distribution: { "5": 600, "4": 350, "3": 200, "2": 70, "1": 27 }
  },
  attributes: {                    // Type-specific (polymorphic)
    battery_life_hours: 30,
    noise_cancelling: true,
    bluetooth_version: "5.2"
  },
  search_tokens: ["wireless", "headphones", "bluetooth", "noise", "cancelling"],
  created_at: ISODate("2026-01-15"),
  updated_at: ISODate("2026-03-17")
}
```

**Indexes:**
```javascript
db.products.createIndex({ category: 1, "price.amount": 1 })        // Faceted search
db.products.createIndex({ brand: 1, "ratings.avg": -1 })            // Brand + rating
db.products.createIndex({ search_tokens: 1 })                        // Keyword search
db.products.createIndex({ slug: 1 }, { unique: true })               // URL lookup
db.products.createIndex({ "inventory.available": 1 })                // Stock queries
```

**Scaling Strategy:**
- **Atlas Search** for full-text search with fuzzy matching
- **Shard key:** `{ category: 1, _id: "hashed" }` — targeted queries + even distribution
- **Computed pattern** for ratings (pre-aggregated, updated on each review)
- **Change Streams** for inventory sync across services
