# Transactions & Consistency

## Read Concerns

**Read concern** controls the consistency and isolation of data returned by read operations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Read Concern Spectrum                               │
│                                                                             │
│   "local"         "available"      "majority"      "linearizable"          │
│    ←──────────────────────────────────────────────────────────────→         │
│   Fastest                                                    Strongest     │
│   (may read                                            (guaranteed to      │
│    uncommitted                                          see all ack'd      │
│    data)                                                writes)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Read Concern | Description | Use Case |
|-------------|-------------|----------|
| `"local"` | Returns most recent data from the node (default). May return data that could be rolled back. | General purpose, single-node reads |
| `"available"` | Like local, but for sharded clusters — may return orphaned documents during chunk migration. Fastest. | Analytics where slight inaccuracy is OK |
| `"majority"` | Returns data acknowledged by majority of replica set members. Guaranteed durable. | Financial data, audit logs |
| `"snapshot"` | Returns data from a snapshot at the start of the transaction. Used within multi-document transactions. | Multi-document transactions |
| `"linearizable"` | Like majority, but also waits for all prior writes to be visible. Most consistent but slowest. Single-document reads only. | Critical reads (account balance checks) |

```javascript
// Set read concern per-operation
db.accounts.find({ user_id: "alice" }).readConcern("majority")

// Set on client connection
const client = new MongoClient(uri, {
  readConcern: { level: "majority" }
})
```

---

## Write Concerns

**Write concern** controls acknowledgment behavior for write operations.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Write Concern Spectrum                               │
│                                                                             │
│   w: 0             w: 1             w: "majority"     w: <n>               │
│    ←──────────────────────────────────────────────────────────────→         │
│   Fire-and-forget  Primary only     Majority of       N replica set        │
│   (no ack)         (default)        members           members              │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Write Concern | Description | Trade-off |
|--------------|-------------|-----------|
| `w: 0` | No acknowledgment (fire and forget) | Fastest, but data may be lost |
| `w: 1` | Acknowledged by primary only (default) | Fast, but data may be lost if primary crashes before replication |
| `w: "majority"` | Acknowledged by majority of replica set members | Durable, but higher latency |
| `w: <n>` | Acknowledged by exactly n members | Custom durability level |
| `j: true` | Wait for journal write (on-disk durability) | Safest, adds ~30ms latency |
| `wtimeout` | Max wait time for write concern | Prevents indefinite blocks |

```javascript
// Write with majority concern + journal
db.accounts.insertOne(
  { user_id: "alice", balance: 1000 },
  { writeConcern: { w: "majority", j: true, wtimeout: 5000 } }
)

// ⚠️ w: "majority" without j: true → data could be in memory but not on disk
// For financial data: always use w: "majority", j: true
```

---

## Read Preferences

**Read preference** determines which replica set member(s) to read from.

```
┌──────────────────────────────────────────────────┐
│              Replica Set                          │
│                                                    │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐ │
│   │ PRIMARY  │     │SECONDARY │     │SECONDARY │ │
│   │  (R/W)   │     │   (R)    │     │   (R)    │ │
│   └──────────┘     └──────────┘     └──────────┘ │
│                                                    │
│   Read Preference determines which node(s) serve  │
│   read operations                                  │
└──────────────────────────────────────────────────┘
```

| Read Preference | Behavior | Use Case |
|----------------|----------|----------|
| `primary` | Always read from primary (default) | Strong consistency required |
| `primaryPreferred` | Primary if available, else secondary | Default with fallback |
| `secondary` | Always read from secondary | Offload reads from primary |
| `secondaryPreferred` | Secondary if available, else primary | Analytics, reporting |
| `nearest` | Lowest network latency member | Geo-distributed, latency-sensitive |

```javascript
// Set read preference
db.getMongo().setReadPref("secondaryPreferred")

// With tag sets (route to specific data center)
db.users.find().readPref("secondary", [{ dc: "east" }])

// ⚠️ Reading from secondary = eventual consistency
// Data may be stale by replication lag (typically < 1 second)
```

---

## Multi-Document ACID Transactions

MongoDB supports **multi-document ACID transactions** since version 4.0 (replica sets) and 4.2 (sharded clusters).

### Single Document Atomicity (No Transaction Needed)

```javascript
// Single document operations are ALWAYS atomic in MongoDB
// No transaction needed for:
db.accounts.updateOne(
  { _id: "alice" },
  {
    $inc: { balance: -100 },
    $push: { transactions: { amount: -100, date: new Date() } }
  }
)
// ✅ Both $inc and $push happen atomically
```

### Multi-Document Transactions

```javascript
// Use when you need atomicity across MULTIPLE documents or collections
const session = client.startSession();

try {
  session.startTransaction({
    readConcern: { level: "snapshot" },
    writeConcern: { w: "majority" },
    readPreference: "primary"
  });

  // Operation 1: Debit from Alice
  await db.accounts.updateOne(
    { _id: "alice", balance: { $gte: 100 } },  // Check sufficient balance
    { $inc: { balance: -100 } },
    { session }
  );

  // Operation 2: Credit to Bob
  await db.accounts.updateOne(
    { _id: "bob" },
    { $inc: { balance: 100 } },
    { session }
  );

  // Operation 3: Log the transfer
  await db.transfers.insertOne(
    {
      from: "alice",
      to: "bob",
      amount: 100,
      timestamp: new Date()
    },
    { session }
  );

  // Commit — all or nothing
  await session.commitTransaction();
  console.log("Transfer completed successfully");

} catch (error) {
  // Abort — rolls back all changes
  await session.abortTransaction();
  console.error("Transfer failed:", error);
} finally {
  session.endSession();
}
```

### Transaction Limitations

| Limitation | Details |
|-----------|---------|
| **Max runtime** | 60 seconds default (`transactionLifetimeLimitSeconds`) |
| **Performance** | Higher latency than non-transactional writes |
| **Lock contention** | Long transactions can block other operations |
| **WiredTiger cache** | Large transactions can pressure cache |
| **DDL operations** | Cannot create/drop collections or indexes in transaction |
| **Capped collections** | Not supported in transactions |
| **Design signal** | If you need many transactions, you may need to redesign your schema |

> **Best Practice:** Use transactions sparingly. Good schema design (embedding related data) eliminates the need for most transactions.

---

## Causal Consistency

**Causal consistency** guarantees that operations that are causally related are seen in the correct order.

```javascript
// Without causal consistency (reading from secondary):
// 1. Write to primary: insert user
// 2. Read from secondary: user NOT found! (replication lag)

// With causal consistency:
const session = client.startSession({ causalConsistency: true });

// Write
await db.users.insertOne({ name: "Alice" }, { session });

// Read — guaranteed to see the write above, even from secondary
const user = await db.users.findOne({ name: "Alice" }, { session });
// ✅ Always finds Alice
```

**How it works:** The session tracks `operationTime` and `clusterTime`. Subsequent reads must wait until the secondary has replicated past the write's timestamp.

---

## Change Streams

Watch real-time changes to collections, databases, or deployments.

```javascript
// Watch a collection for changes
const changeStream = db.orders.watch();

changeStream.on("change", (change) => {
  console.log("Change detected:", change);
  // change.operationType: "insert", "update", "replace", "delete"
  // change.fullDocument: the changed document (for insert/replace)
  // change.updateDescription: { updatedFields, removedFields }
});

// Watch with pipeline filters
const pipeline = [
  { $match: { "fullDocument.status": "critical" } }
];
const changeStream = db.alerts.watch(pipeline);

// Watch with options
const changeStream = db.orders.watch([], {
  fullDocument: "updateLookup",  // Include full document on updates
  resumeAfter: resumeToken       // Resume from a specific point
});

// Resume after disconnect
let resumeToken = null;
changeStream.on("change", (change) => {
  resumeToken = change._id;  // Store resume token
  processChange(change);
});

// On reconnect:
const newStream = db.orders.watch([], { resumeAfter: resumeToken });
```

**Use Cases:**
- Real-time notifications
- Cache invalidation
- Data synchronization between services
- Event-driven architectures
- ETL / data pipelines

---

## Consistency Models Comparison

| Scenario | Read Concern | Write Concern | Read Pref | Guarantee |
|----------|-------------|--------------|-----------|-----------|
| **Speed priority** | `local` | `w: 1` | `nearest` | Fastest, lowest consistency |
| **General purpose** | `local` | `w: 1` | `primary` | Good balance (default) |
| **Read-heavy analytics** | `local` | `w: 1` | `secondaryPreferred` | Offload primary |
| **Financial / Critical** | `majority` | `w: "majority", j: true` | `primary` | Strong consistency + durability |
| **Strongest** | `linearizable` | `w: "majority", j: true` | `primary` | Strongest possible |

---

## Interview Questions — Transactions & Consistency

### Q1: Does MongoDB support ACID transactions?

**Yes, since MongoDB 4.0** (replica sets) and **4.2** (sharded clusters).

- **Single-document** operations have always been atomic
- **Multi-document** transactions provide full ACID:
  - **Atomicity** — all or nothing
  - **Consistency** — validation rules enforced
  - **Isolation** — snapshot isolation (reads see consistent snapshot)
  - **Durability** — with `w: "majority"` + `j: true`

### Q2: What's the difference between `read concern: "majority"` and `"linearizable"`?

| Aspect | `"majority"` | `"linearizable"` |
|--------|-------------|-----------------|
| Guarantee | Data is durable (won't be rolled back) | Data is durable AND reflects all prior writes |
| Scope | Multi-document | Single-document only |
| Performance | Moderate overhead | High overhead (confirmation from majority) |
| Use case | Financial records | Real-time balance checks |

`linearizable` = `majority` + **recency guarantee** (no stale reads).

### Q3: Why should transactions be a last resort in MongoDB?

1. **Performance:** Transactions add latency (locking, coordination overhead)
2. **Concurrency:** Long-held locks reduce throughput
3. **Complexity:** Error handling, retries, timeouts
4. **Design smell:** Needing many transactions often means your schema isn't leveraging MongoDB's document model
5. **Better alternative:** Embed related data in a single document → single-document atomicity (free!)

### Q4: How do Change Streams work under the hood?

1. Built on top of the **oplog** (replication log)
2. Tailable cursor on the oplog, filtered to relevant collection
3. Return change events with resume tokens
4. **Require:** replica set (or sharded cluster) — don't work on standalone
5. Can survive network interruptions via resume tokens
6. Pre-images and post-images available (MongoDB 6.0+)
