# Distributed Storage

## Storage Engine Internals

### B-Trees (Traditional RDBMS)

Used for **read-heavy** workloads (PostgreSQL, MySQL, SQL Server).

```
B-Tree Structure (order 3):
                    ┌───────────┐
                    │  [30, 60]  │              ← Root
                    └─┬───┬───┬─┘
                      │   │   │
            ┌─────────┘   │   └──────────┐
            ▼             ▼              ▼
       ┌─────────┐  ┌──────────┐   ┌─────────┐
       │ [10, 20]│  │ [40, 50] │   │ [70, 80]│  ← Internal nodes
       └─┬──┬──┬─┘  └─┬──┬──┬─┘   └─┬──┬──┬─┘
         │  │  │       │  │  │       │  │  │
         ▼  ▼  ▼       ▼  ▼  ▼       ▼  ▼  ▼
       Data pages with records              ← Leaf nodes

Properties:
  - Balanced tree → O(log n) reads AND writes
  - Pages are fixed-size (typically 4-16 KB)
  - In-place updates (modify pages on disk)
  - Good for point queries and range queries
```

### LSM Trees (Log-Structured Merge Trees)

Used for **write-heavy** workloads (Cassandra, RocksDB, LevelDB, HBase).

```
Write Path:
  1. Write → WAL (Write-Ahead Log) on disk (durability)
  2. Write → Memtable (in-memory sorted tree)
  3. When Memtable is full → flush to SSTable on disk
  4. Background: compact + merge SSTables

  ┌───────────────┐
  │   Memtable     │  ← In-memory (AVL tree / skiplist)
  │  (sorted)      │
  └───────┬───────┘
          │ flush when full
          ▼
  ┌───────────────┐
  │  Level 0       │  ← Recent SSTables (may overlap)
  │ [SST][SST]    │
  └───────┬───────┘
          │ compaction (merge-sort)
          ▼
  ┌───────────────┐
  │  Level 1       │  ← Merged, non-overlapping SSTables
  │ [  SSTable   ] │
  └───────┬───────┘
          │ compaction
          ▼
  ┌───────────────┐
  │  Level 2       │  ← Larger, non-overlapping
  │ [    SSTable     ] │
  └───────────────┘

Read Path:
  1. Check Memtable (fastest)
  2. Check Bloom filters for each SSTable level
  3. Binary search within matching SSTable
  → Reads slower than B-Tree (must check multiple levels)
```

### B-Tree vs LSM-Tree Comparison

| Aspect | B-Tree | LSM-Tree |
|--------|--------|----------|
| **Write speed** | Moderate (in-place update + WAL) | Fast (sequential append) |
| **Read speed** | Fast (single tree traversal) | Slower (check multiple levels) |
| **Write amplification** | Lower (1 page write) | Higher (compaction rewrites) |
| **Space amplification** | Lower | Higher (multiple copies during compaction) |
| **Best for** | Read-heavy, OLTP | Write-heavy, time-series, logs |
| **Used by** | PostgreSQL, MySQL, MongoDB | Cassandra, RocksDB, LevelDB |

---

## Distributed File Systems

### Google File System (GFS) / HDFS

```
┌──────────────┐
│   Client      │
└──────┬───────┘
       │ 1. "Where is file X?"
       ▼
┌──────────────┐
│  Master /     │  Metadata: file → chunk mapping
│  NameNode     │  Chunk locations, replication
└──────┬───────┘
       │ 2. "Chunks at servers A, B, C"
       ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ChunkServer│  │ChunkServer│  │ChunkServer│
│ (DataNode)│  │ (DataNode)│  │ (DataNode)│
│           │  │           │  │           │
│ Chunk 1   │  │ Chunk 1   │  │ Chunk 2   │
│ Chunk 3   │  │ Chunk 2   │  │ Chunk 3   │
└──────────┘  └──────────┘  └──────────┘

Properties:
  - Files split into large chunks (64 MB HDFS, 64 MB GFS)
  - Each chunk replicated 3x across different nodes/racks
  - Master is SPOF (mitigated by standby in HDFS HA)
  - Optimized for large sequential reads/writes
  - NOT suitable for low-latency random access
```

### Object Storage (S3, GCS, Azure Blob)

```
Properties:
  - Flat namespace (no directories, just key-value)
  - Immutable objects (no in-place updates, only replace)
  - Virtually unlimited scale
  - High durability (11 9's — 99.999999999%)
  - Eventually consistent reads (S3 now strongly consistent)
  - Cheap storage, expensive operations

Use cases:
  - Data lake storage (Parquet, ORC files)
  - Backups and archives
  - Static file serving (images, videos)
  - ML training data
```

---

## Distributed Databases

### Cassandra (AP, Wide-Column)

```
Architecture:
  - Leaderless (peer-to-peer, no master)
  - Consistent hashing with vnodes
  - Tunable consistency: ONE, QUORUM, ALL
  - LSM-tree storage engine

Data Model:
  Table: user_activity
  Partition Key: user_id
  Clustering Key: timestamp (sorted within partition)

  ┌─────────────┬───────────────────┬────────┐
  │ user_id (PK)│ timestamp (CK)    │ action │
  ├─────────────┼───────────────────┼────────┤
  │ alice       │ 2026-03-17 10:00  │ login  │
  │ alice       │ 2026-03-17 10:05  │ search │
  │ bob         │ 2026-03-17 09:00  │ login  │
  └─────────────┴───────────────────┴────────┘

Best for:
  - High write throughput (time-series, IoT, logs)
  - Multi-datacenter replication
  - Simple query patterns (key-based)

Not for:
  - Complex queries (joins, aggregations)
  - Strong consistency requirements
  - Frequently changing schema
```

### DynamoDB (AP/CP configurable, Key-Value + Document)

```
Architecture:
  - Managed by AWS (serverless)
  - Consistent hashing with auto-splitting
  - Single-digit millisecond latency at any scale

Data Model:
  - Partition Key (required) + Sort Key (optional)
  - Global Secondary Indexes (GSI)
  - Local Secondary Indexes (LSI)

Capacity:
  - Provisioned: set read/write capacity units
  - On-demand: auto-scales (pay per request)

DynamoDB Streams:
  - CDC (Change Data Capture) — like Kafka
  - Trigger Lambda functions on data changes

Best for:
  - Serverless applications
  - Session stores, shopping carts
  - High-scale, low-latency key-value access
  - Event-driven architectures (with Streams)
```

### CockroachDB (CP, NewSQL)

```
Architecture:
  - Distributed SQL (PostgreSQL wire protocol)
  - Raft consensus per-range (strong consistency)
  - Serializable isolation (strongest!)
  - Automatic sharding and rebalancing

Data Model:
  - Standard SQL tables
  - Distributed transactions (same API as PostgreSQL)

  CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    total DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT now()
  );

Best for:
  - SQL workloads that need horizontal scaling
  - Multi-region with strong consistency
  - Financial/transactional applications
  - PostgreSQL migrations that need scale
```

### Database Comparison

| Feature | Cassandra | DynamoDB | CockroachDB | MongoDB | PostgreSQL |
|---------|-----------|----------|-------------|---------|-----------|
| **Model** | Wide-column | Key-Value + Doc | Relational (SQL) | Document | Relational (SQL) |
| **Consistency** | Tunable (AP default) | Tunable (eventual/strong) | Strong (CP) | Configurable | Strong (CP) |
| **Scaling** | Horizontal (leaderless) | Horizontal (managed) | Horizontal (Raft) | Horizontal (sharding) | Vertical (+ read replicas) |
| **Transactions** | Limited (lightweight) | Limited (single table) | Full ACID (distributed) | Multi-doc ACID | Full ACID |
| **Best for** | Write-heavy, time-series | Serverless, AWS-native | SQL at scale | Flexible schema | Complex queries, OLTP |

---

## Data Lake vs Data Warehouse

```
DATA WAREHOUSE:                   DATA LAKE:
  Structured data only              Any data (structured, semi, unstructured)
  Schema-on-write                   Schema-on-read
  Star/snowflake schema             Raw storage (files/objects)
  SQL queries                       SQL + Spark + ML
  Expensive storage                 Cheap storage (S3)
  Fast queries                      Slower (depends on engine)
  
  Examples:                         Examples:
  - Snowflake                       - S3 + Athena
  - BigQuery                        - Delta Lake (Databricks)
  - Redshift                        - Apache Iceberg
  - Synapse                         - Apache Hudi
```

---

## Interview Questions — Distributed Storage

### Q1: When would you use LSM-trees vs B-trees?

| Scenario | Choose |
|----------|--------|
| Write-heavy workload (IoT, logs, events) | **LSM-tree** (sequential writes) |
| Read-heavy workload (OLTP) | **B-tree** (single traversal) |
| Range queries important | **Both work** (B-tree slightly better) |
| Storage efficiency critical | **B-tree** (lower space amplification) |
| Write throughput critical | **LSM-tree** (higher write throughput) |

### Q2: How does Cassandra achieve high write throughput?

1. **Leaderless** — any node accepts writes (no single-leader bottleneck)
2. **LSM-tree** — writes go to memtable (in-memory), then flush to SSTables (sequential I/O)
3. **Append-only** — no random disk seeks for writes
4. **Tunable consistency** — write to 1 node (`ONE`) for max speed, or quorum for durability
5. **Ring topology** — consistent hashing distributes writes evenly

### Q3: What is a significant drawback of Cassandra?

**Limited query flexibility.** You must design tables around your query patterns:
- No JOINs
- No ad-hoc queries on non-indexed columns
- Must denormalize data (store multiple copies organized by different keys)
- Changing query patterns requires restructuring tables

### Q4: CockroachDB vs Cassandra — when to use each?

| Requirement | CockroachDB | Cassandra |
|------------|-------------|-----------|
| Need SQL + JOINs | ✅ | ❌ |
| Need ACID transactions | ✅ | Limited |
| Write-heavy (millions/sec) | Moderate | ✅ |
| Strong consistency | ✅ | Configurable |
| Multi-region | ✅ (Raft-based) | ✅ (leaderless) |
| Operational simplicity | Moderate | Complex |
