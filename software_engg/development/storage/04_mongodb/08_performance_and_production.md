# Performance & Production

## WiredTiger Storage Engine

MongoDB's default storage engine since 3.2. Understanding WiredTiger is key to performance tuning.

```
┌──────────────────────────────────────────────────────┐
│                    WiredTiger                         │
│                                                      │
│  ┌──────────────┐     ┌──────────────┐              │
│  │ Internal Cache│     │ File System   │              │
│  │  (WT Cache)  │ ←→  │    Cache     │ ←→  Disk     │
│  │              │     │ (OS Page Cache)│              │
│  │ Default: 50% │     │              │              │
│  │ of RAM - 1GB │     │ Transparent  │              │
│  └──────────────┘     └──────────────┘              │
│                                                      │
│  ┌──────────────┐     ┌──────────────┐              │
│  │  Compression │     │   Journaling  │              │
│  │  snappy(data)│     │  (WAL, 100ms │              │
│  │  prefix(idx) │     │   checkpoint) │              │
│  └──────────────┘     └──────────────┘              │
└──────────────────────────────────────────────────────┘
```

### Key WiredTiger Concepts

| Concept | Description |
|---------|-------------|
| **Internal Cache** | In-memory storage for frequently accessed data. Default: 50% of (RAM - 1 GB), minimum 256 MB |
| **Compression** | Data: `snappy` (default), indexes: `prefix` compression. Can use `zlib`, `zstd` |
| **Journaling** | Write-ahead log for crash recovery. Commits every 100ms |
| **Checkpoints** | Full data flush to disk every 60 seconds |
| **Document-level Locking** | Concurrent reads/writes on different documents |
| **MVCC** | Multi-Version Concurrency Control — readers don't block writers |

```javascript
// Check WiredTiger cache usage
db.serverStatus().wiredTiger.cache
// Key metrics:
// - "bytes currently in the cache"
// - "maximum bytes configured"
// - "tracked dirty bytes in the cache"
// - "pages evicted by application threads"  ← if high, cache is too small

// Configure cache size
// mongod.conf:
// storage:
//   wiredTiger:
//     engineConfig:
//       cacheSizeGB: 4

// Change compression
db.createCollection("logs", {
  storageEngine: {
    wiredTiger: {
      configString: "block_compressor=zstd"
    }
  }
})
```

---

## Connection Pooling

Drivers maintain a **connection pool** to avoid the overhead of creating new connections per operation.

```javascript
// Node.js driver connection pool settings
const client = new MongoClient(uri, {
  maxPoolSize: 100,          // Max connections in pool (default: 100)
  minPoolSize: 10,           // Min connections kept alive (default: 0)
  maxIdleTimeMS: 30000,      // Close idle connections after 30s
  waitQueueTimeoutMS: 10000, // Timeout waiting for connection from pool
  connectTimeoutMS: 10000,   // Timeout for initial connection
  socketTimeoutMS: 30000,    // Timeout for socket operations
  serverSelectionTimeoutMS: 30000  // Timeout finding suitable server
})

// Monitor connections
db.serverStatus().connections
// {
//   "current": 42,           ← Active connections
//   "available": 51158,      ← Remaining available
//   "totalCreated": 1234     ← Total connections created since start
// }
```

### Connection Pool Sizing

```
Rule of thumb:
  Pool size = Number of concurrent operations needed

For web servers:
  Pool size ≈ Number of worker threads/processes

∑ Pool sizes across all app instances ≤ mongod max connections (default: 65536)
```

---

## Query Profiler

The **profiler** captures slow queries for analysis.

```javascript
// Set profiling level
db.setProfilingLevel(0)  // Off (default)
db.setProfilingLevel(1, { slowms: 100 })  // Log queries > 100ms
db.setProfilingLevel(2)  // Log ALL queries (⚠️ performance impact)

// Check current level
db.getProfilingStatus()

// View profiled queries
db.system.profile.find().sort({ ts: -1 }).limit(5)

// Find slowest queries
db.system.profile.find({
  millis: { $gt: 100 }
}).sort({ millis: -1 }).limit(10)

// Find queries with collection scans
db.system.profile.find({
  "planSummary": "COLLSCAN"
}).sort({ millis: -1 })

// Find specific collection's slow queries
db.system.profile.find({
  ns: "mydb.orders",
  millis: { $gt: 50 }
})

// Profile output example:
{
  "op": "query",
  "ns": "mydb.orders",
  "command": { "find": "orders", "filter": { "status": "shipped" } },
  "keysExamined": 0,          // No index used!
  "docsExamined": 1000000,    // Full collection scan!
  "nreturned": 500,
  "millis": 2500,             // 2.5 seconds
  "planSummary": "COLLSCAN",  // No index
  "ts": ISODate("2026-03-17T10:30:00Z")
}
```

---

## Memory Management

### Working Set

The **working set** = data and indexes frequently accessed. Ideally fits entirely in RAM.

```javascript
// Check data and index sizes
db.stats()
// {
//   "dataSize": 5368709120,        // 5 GB data
//   "storageSize": 2147483648,     // 2 GB on disk (compressed)
//   "indexSize": 536870912,        // 512 MB indexes
//   "totalSize": 2684354560        // Total storage
// }

// Per-collection stats
db.orders.stats()
db.orders.totalSize()
db.orders.totalIndexSize()

// Server memory
db.serverStatus().mem
// {
//   "resident": 4096,    // 4 GB resident
//   "virtual": 8192,     // 8 GB virtual
//   "mapped": 0
// }
```

### Memory Optimization

```
1. Index size < WiredTiger cache (indexes must fit in RAM!)
   - If total index size > cache → index swapping → slow queries

2. Reduce document size
   - Use short field names in high-volume collections
   - Remove unused fields
   - Use appropriate BSON types (int32 vs int64 vs string)

3. Use projection
   db.users.find({}, { name: 1, email: 1 })  // Only fetch needed fields

4. Use covered queries
   - All fields from index, no document fetch needed

5. Compact collections
   db.runCommand({ compact: "orders" })       // Reclaim disk space
```

---

## Monitoring

### Key Metrics to Monitor

| Category | Metric | Target |
|----------|--------|--------|
| **Operations** | opcounters (insert/query/update/delete/command) | Baseline + alerting |
| **Connections** | Current connections vs available | < 80% of max |
| **Memory** | Resident memory, cache usage | Working set fits in RAM |
| **Replication** | Replication lag (seconds behind) | < 1 second |
| **Disk** | IOPS, disk utilization, free space | < 80% utilization |
| **Locks** | Lock % (read/write) | < 5% |
| **Network** | Network in/out bytes | Baseline + alerting |
| **Cursors** | Open cursors, timed out cursors | Low timed-out count |
| **Query** | Slow queries (profiler), COLLSCAN count | 0 COLLSCAN in production |

```javascript
// Server status (comprehensive)
db.serverStatus()

// Current operations
db.currentOp()
// Find long-running operations
db.currentOp({ "secs_running": { $gt: 5 } })

// Kill a long-running operation
db.killOp(opId)

// mongostat — real-time stats (like top for MongoDB)
// Run from command line:
// mongostat --host localhost:27017

// mongotop — track time spent per collection
// Run from command line:
// mongotop --host localhost:27017
```

---

## Security

### Authentication

```javascript
// Enable authentication in mongod.conf
// security:
//   authorization: enabled

// Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "securePassword123!",
  roles: [{ role: "root", db: "admin" }]
})

// Create application user
use mydb
db.createUser({
  user: "app_user",
  pwd: "appPassword456!",
  roles: [
    { role: "readWrite", db: "mydb" },
    { role: "read", db: "analytics" }
  ]
})

// Connect with auth
// mongosh -u app_user -p appPassword456! --authenticationDatabase mydb
```

### Built-in Roles

| Role | Scope | Permissions |
|------|-------|-------------|
| `read` | Database | Read all non-system collections |
| `readWrite` | Database | Read + Write |
| `dbAdmin` | Database | Index management, stats, validation |
| `userAdmin` | Database | Create/modify users and roles |
| `clusterAdmin` | Cluster | Sharding, replication management |
| `root` | All | Superuser (all privileges) |

### Encryption

```yaml
# mongod.conf — TLS/SSL
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb.pem
    CAFile: /etc/ssl/ca.pem

# Encryption at rest (Enterprise)
security:
  enableEncryption: true
  encryptionKeyFile: /etc/mongodb/encryption-key
```

### Network Security

```yaml
# Bind to specific IP (don't bind to 0.0.0.0 in production!)
net:
  bindIp: 127.0.0.1,10.0.1.100
  port: 27017

# Firewall: only allow app servers to connect to MongoDB port
```

---

## Backup & Restore

### mongodump / mongorestore

```bash
# Full database backup
mongodump --uri="mongodb://user:pass@host:27017/mydb" --out=/backup/2026-03-17

# Specific collection
mongodump --db=mydb --collection=orders --out=/backup/orders

# With compression
mongodump --gzip --archive=/backup/mydb.gz

# Restore
mongorestore --uri="mongodb://user:pass@host:27017" /backup/2026-03-17

# Restore specific collection
mongorestore --db=mydb --collection=orders /backup/orders/mydb/orders.bson

# Restore from compressed archive
mongorestore --gzip --archive=/backup/mydb.gz
```

### Continuous Backup with Oplog

```bash
# Dump with oplog for point-in-time recovery
mongodump --oplog --out=/backup/2026-03-17

# Restore with oplog replay
mongorestore --oplogReplay /backup/2026-03-17
```

### MongoDB Atlas Backup

```
Atlas provides:
- Continuous backups (oplog-based, point-in-time recovery)
- Cloud provider snapshots
- Backup policies (retention, frequency)
- One-click restore to any point in time
```

---

## Production Configuration Checklist

### mongod.conf Example

```yaml
storage:
  dbPath: /data/db
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4           # Set based on available RAM
    collectionConfig:
      blockCompressor: snappy
    indexConfig:
      prefixCompression: true

systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  logRotate: rename

net:
  port: 27017
  bindIp: 10.0.1.100          # Internal IP only
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb.pem

security:
  authorization: enabled

replication:
  replSetName: production-rs
  oplogSizeMB: 2048           # Size based on write volume

operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100

setParameter:
  maxIndexBuildMemoryUsageMegabytes: 500
```

### Production Checklist

| Category | Checklist |
|----------|-----------|
| **Hardware** | ✅ Use SSDs for storage, ✅ RAM > working set size |
| **Security** | ✅ Enable auth, ✅ TLS/SSL, ✅ Bind to internal IPs, ✅ Firewall rules |
| **Replication** | ✅ 3+ member replica set, ✅ Monitor replication lag |
| **Storage** | ✅ Enable journaling, ✅ Separate drives for data + journal |
| **Monitoring** | ✅ Monitor disk, memory, connections, slow queries |
| **Backup** | ✅ Automated backups, ✅ Test restores regularly |
| **Indexes** | ✅ Create indexes before going live, ✅ Drop unused indexes |
| **OS** | ✅ Disable transparent huge pages, ✅ Increase file descriptors (ulimit) |

---

## MongoDB Atlas

**Atlas** is MongoDB's fully managed cloud database service.

| Feature | Description |
|---------|-------------|
| **Free Tier** | 512 MB storage, shared cluster (M0) |
| **Auto-scaling** | Compute and storage auto-scaling |
| **Global Clusters** | Multi-region, zone-sharded deployments |
| **Atlas Search** | Full-text search powered by Lucene |
| **Atlas Data Federation** | Query data across Atlas + S3 + HTTP |
| **Charts** | Built-in data visualization |
| **Triggers** | Serverless functions triggered by database events |
| **Realm (App Services)** | Backend-as-a-service (auth, sync, functions) |

---

## Interview Questions — Performance

### Q1: How would you optimize a slow MongoDB deployment?

**Systematic approach:**

1. **Identify slow queries** → Enable profiler (`slowms: 100`), check `system.profile`
2. **Add indexes** → Use `explain()` to find COLLSCAN queries, create targeted compound indexes
3. **Check working set** → Ensure data + index fit in RAM (check `wiredTiger.cache` stats)
4. **Optimize schema** → Embed data read together, use the Subset pattern for large documents
5. **Use projections** → Only return fields you need
6. **Connection pool** → Tune pool size to avoid connection overhead
7. **Scale** → Replica set for read scaling, sharding for write scaling

### Q2: What is the WiredTiger cache and how do you size it?

- **Default:** 50% of (total RAM - 1 GB) or 256 MB (whichever is larger)
- Stores frequently-accessed documents and index data in memory
- If cache is too small → excess evictions → high disk I/O → slow queries
- **Sizing:** Monitor `"pages evicted by application threads"` — if high, increase cache
- Don't set > 80% of RAM (OS needs memory too)

### Q3: How do you handle MongoDB backups for a large production database?

**Strategy depends on scale:**

| Method | Pros | Cons |
|--------|------|------|
| `mongodump` | Simple, works everywhere | Slow for large DBs, locks during dump |
| Filesystem snapshots (LVM/EBS) | Fast, consistent | Requires journaling, cloud-specific |
| Atlas continuous backup | Point-in-time recovery, automatic | Atlas-only, costs more |
| Oplog-based backup | Continuous, minimal overhead | Complex setup |

**Best practices:**
- Test restores regularly (backup that can't be restored is worthless)
- Backup from a secondary (don't impact primary)
- Store backups in different region/account
- Monitor backup size growth
