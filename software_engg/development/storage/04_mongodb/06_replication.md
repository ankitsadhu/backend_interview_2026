# Replication in MongoDB

## What is a Replica Set?

A **replica set** is a group of `mongod` instances that maintain the same data set, providing **redundancy**, **high availability**, and **automatic failover**.

```
┌────────────────────────────────────────────────────────────────┐
│                        Replica Set                             │
│                                                                │
│   ┌──────────────┐    replication    ┌──────────────┐         │
│   │   PRIMARY     │ ──────────────→  │  SECONDARY   │         │
│   │   (Read/Write)│                  │  (Read-only) │         │
│   │               │    replication   │              │         │
│   │   Accepts all │ ──────────────→  ├──────────────┤         │
│   │   write ops   │                  │  SECONDARY   │         │
│   │               │                  │  (Read-only) │         │
│   └──────────────┘                  └──────────────┘         │
│          ▲                                                     │
│          │ Writes                                              │
│     Application                                                │
└────────────────────────────────────────────────────────────────┘

Minimum: 3 members (1 primary + 2 secondaries)
Recommended: Odd number of voting members for clear elections
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Primary** | Only member that accepts write operations |
| **Secondary** | Maintains copy of primary's data via oplog replication |
| **Failover** | If primary goes down, secondaries hold election to choose new primary |
| **Heartbeat** | Members ping each other every 2 seconds to detect failures |
| **Election** | Fault-tolerant process to choose new primary (Raft-like protocol) |

---

## The Oplog (Operations Log)

The **oplog** is a capped collection (`local.oplog.rs`) that records all write operations on the primary. Secondaries replicate by tailing the oplog.

```
Primary writes:
  INSERT {name: "Alice"} ──→ oplog entry: {op: "i", ns: "mydb.users", o: {name: "Alice"}}
  UPDATE {age: 31}       ──→ oplog entry: {op: "u", ns: "mydb.users", o2: {_id: ...}, o: {$set: {age: 31}}}
  DELETE {_id: ...}      ──→ oplog entry: {op: "d", ns: "mydb.users", o: {_id: ...}}

Secondary tails the oplog and replays operations:
  ┌──────────┐     read oplog     ┌──────────┐
  │  PRIMARY  │ ← ─ ─ ─ ─ ─ ─ ─  │SECONDARY │
  │           │                    │           │
  │  oplog:   │    apply ops      │  data:    │
  │  [i,u,d]  │ ─ ─ ─ ─ ─ ─ ─ → │  [synced] │
  └──────────┘                    └──────────┘
```

### Oplog Details

```javascript
// View oplog entries
use local
db.oplog.rs.find().sort({ $natural: -1 }).limit(5)

// Check oplog size and window
db.getReplicationInfo()
// {
//   "logSizeMB": 1024,
//   "timeDiff": 172800,        // 48 hours of oplog data
//   "tFirst": "...",
//   "tLast": "...",
//   ...
// }

// Check replication lag
rs.printReplicationInfo()
rs.printSecondaryReplicationInfo()
```

**Oplog window** = how far back the oplog goes. If a secondary falls behind more than the oplog window, it needs a **full resync** (copies all data from primary).

---

## Replica Set Configuration

```javascript
// Initialize a replica set
rs.initiate({
  _id: "myReplicaSet",
  members: [
    { _id: 0, host: "mongo1:27017" },
    { _id: 1, host: "mongo2:27017" },
    { _id: 2, host: "mongo3:27017" }
  ]
})

// Check replica set status
rs.status()

// Check current config
rs.conf()

// Add a member
rs.add("mongo4:27017")

// Remove a member
rs.remove("mongo4:27017")

// Step down primary (trigger election)
rs.stepDown(60)  // Step down for 60 seconds
```

---

## Member Types

### Standard Members (Voting)

Regular members that can become primary and participate in elections.

### Priority Settings

```javascript
// Set member priorities (higher = more likely to become primary)
cfg = rs.conf()
cfg.members[0].priority = 10   // Preferred primary
cfg.members[1].priority = 5    // Backup primary
cfg.members[2].priority = 1    // Last resort
rs.reconfig(cfg)

// Priority 0 = can NEVER become primary
cfg.members[2].priority = 0    // Always stays secondary
```

### Arbiter

**Votes in elections but holds NO data**. Used to break ties in even-member sets.

```javascript
rs.addArb("mongo-arbiter:27017")

// Set configuration:
// Primary (1 vote) + Secondary (1 vote) + Arbiter (1 vote) = 3 votes
```

**⚠️ Limitations:**
- No data redundancy benefit (doesn't store data)
- Not recommended in production — use a 3-member set instead
- Cannot become primary
- Don't use more than one arbiter

### Hidden Members

```javascript
// Hidden member: not visible to clients, excluded from read preference routing
cfg = rs.conf()
cfg.members[2].hidden = true
cfg.members[2].priority = 0    // Must be priority 0
rs.reconfig(cfg)

// Use cases:
// - Dedicated backup member
// - Running analytics queries without affecting production reads
// - Reporting workloads
```

### Delayed Members

```javascript
// Delayed member: replicates data with a time delay
cfg = rs.conf()
cfg.members[2].secondaryDelaySecs = 3600  // 1 hour delay
cfg.members[2].hidden = true               // Should be hidden
cfg.members[2].priority = 0               // Can't become primary
rs.reconfig(cfg)

// Use cases:
// - Protection against accidental data deletion
// - "Undo" window — recover data from the delayed member
// - Rolling back application-level errors
```

---

## Elections & Failover

### How Elections Work

```
1. Primary fails (heartbeat timeout: 10 seconds)
       │
       ▼
2. Secondaries detect missing heartbeats
       │
       ▼
3. Eligible member calls for election
   (highest priority, most up-to-date)
       │
       ▼
4. Voting members vote (majority needed)
   - 3-member set: needs 2 votes
   - 5-member set: needs 3 votes
       │
       ▼
5. Winner becomes new primary
   (typically < 12 seconds total)
       │
       ▼
6. Old primary (when it comes back) joins as secondary
```

### Election Eligibility

A member can become primary if:
1. **Priority > 0**
2. **Not hidden or delayed**
3. **Has the most recent oplog entry** (or close to it)
4. **Can reach a majority** of voting members
5. **Is not too far behind** the latest oplog

### Election Triggers

| Trigger | Description |
|---------|-------------|
| Primary failure | Heartbeat timeout (10s) |
| `rs.stepDown()` | Manual step-down |
| Network partition | Primary can't reach majority |
| Priority change | Higher-priority member catches up |
| Maintenance | Rolling restart/upgrade |

---

## Failover Behavior

```javascript
// During failover (typically 10-12 seconds):
// - No writes possible (no primary)
// - Reads from secondaries still work (if read preference allows)
// - Drivers automatically detect new primary (retryable writes)

// Enable retryable writes (default in drivers since 4.2)
const client = new MongoClient(uri, { retryWrites: true });

// Application should handle temporary write failures:
try {
  await collection.insertOne(doc);
} catch (error) {
  if (error.code === 112) {  // WriteConflict
    // Retry the operation
  }
}
```

### Rollbacks

When a failed primary comes back and has writes that weren't replicated:

```
Before failure:
  Primary: [A, B, C, D, E]    ← wrote D, E before crash
  Secondary: [A, B, C]         ← only replicated up to C

After election (Secondary becomes Primary):
  New Primary: [A, B, C, F, G]  ← new writes F, G
  Old Primary: [A, B, C, D, E]  ← D, E conflict!

Rollback:
  Old Primary rolls back D, E → saves to rollback files
  Old Primary syncs from new primary → [A, B, C, F, G]
```

**Prevent rollbacks:** Use `w: "majority"` write concern — writes only acknowledged after majority replication.

---

## Replica Set Read Scaling

```javascript
// Distribute reads across secondaries
// ⚠️ Reads may return stale data (replication lag)

// Read from secondary
db.users.find().readPref("secondary")

// Read from nearest (lowest latency)
db.users.find().readPref("nearest")

// With tag sets (route to specific data center)
rs.reconfig({
  members: [
    { _id: 0, host: "mongo1:27017", tags: { dc: "east", usage: "production" } },
    { _id: 1, host: "mongo2:27017", tags: { dc: "east", usage: "analytics" } },
    { _id: 2, host: "mongo3:27017", tags: { dc: "west", usage: "production" } }
  ]
})

// Read only from analytics nodes
db.reports.find().readPref("secondary", [{ usage: "analytics" }])
```

---

## Monitoring Replication

```javascript
// Replica set status
rs.status()
// Key fields:
// - members[].stateStr: "PRIMARY", "SECONDARY", "ARBITER"
// - members[].health: 1 (up) or 0 (down)
// - members[].optime: last operation timestamp
// - members[].lastHeartbeat: last heartbeat time

// Replication lag
rs.printSecondaryReplicationInfo()
// Shows seconds behind primary for each secondary

// Oplog info
rs.printReplicationInfo()
// Shows oplog size and time range
```

---

## Interview Questions — Replication

### Q1: What happens during a MongoDB failover?

1. Primary becomes unreachable (heartbeat timeout: 10 seconds)
2. Remaining members detect failure via missing heartbeats
3. Eligible secondary with highest priority and most recent data calls election
4. Majority vote required (e.g., 2 of 3 members)
5. Winner becomes new primary (total time: ~10-12 seconds)
6. Drivers automatically discover new primary
7. Old primary rejoins as secondary (may rollback unreplicated writes)

**Application impact:** Brief period (seconds) with no write availability. Reads from secondaries unaffected.

### Q2: How does MongoDB handle split-brain?

**Split-brain prevention:** A member can only become primary if it can reach a **majority** of voting members.

```
Network partition example (5-member set):
  Partition A: [M1, M2]     ← 2 members, not majority (need 3)
  Partition B: [M3, M4, M5] ← 3 members, IS majority

  → Only Partition B can elect a primary
  → Partition A has NO primary (cannot accept writes)
  → No split-brain: at most ONE primary exists at any time
```

### Q3: Why use an odd number of members in a replica set?

To ensure a **clear majority** in elections:
- 3 members → need 2 votes → tolerates 1 failure
- 4 members → need 3 votes → still tolerates only 1 failure (paying for extra member with no benefit)
- 5 members → need 3 votes → tolerates 2 failures

**Odd numbers are more cost-effective** for the same fault tolerance.

### Q4: What is replication lag and how do you minimize it?

**Replication lag** = time delay between a write on the primary and when it appears on secondaries.

**Causes:**
- Network latency between members
- Disk I/O bottlenecks on secondaries
- Large batch operations on primary
- Heavy read load on secondaries

**Mitigation:**
- Place members in same data center (low latency)
- Use faster disks (SSD) on secondaries
- Avoid large bulk writes without batching
- Monitor with `rs.printSecondaryReplicationInfo()`
- Use `w: "majority"` to ensure writes replicate before acknowledgment
