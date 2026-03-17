# MongoDB Study Guide

> Comprehensive MongoDB learning path from beginner to advanced, organized for interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | What is MongoDB, document model, BSON, CRUD operations, data types, shell basics, `mongosh` usage | 🟢 Beginner |
| 02 | [Schema Design](./02_schema_design.md) | Embedding vs referencing, one-to-one/one-to-many/many-to-many patterns, schema validation, anti-patterns, design patterns (Bucket, Outlier, Computed, Subset, Polymorphic) | 🟢🟡 Beginner-Intermediate |
| 03 | [Indexing](./03_indexing.md) | Single-field, compound, multikey, text, geospatial, wildcard, partial, sparse, TTL indexes, `explain()`, index strategies | 🟡 Intermediate |
| 04 | [Aggregation Framework](./04_aggregation.md) | Pipeline stages ($match, $group, $project, $lookup, $unwind, $facet, $bucket, $graphLookup), expressions, optimization | 🟡 Intermediate |
| 05 | [Transactions & Consistency](./05_transactions.md) | Read/write concerns, read preferences, multi-document ACID transactions, causal consistency, sessions | 🟡🔴 Intermediate-Advanced |
| 06 | [Replication](./06_replication.md) | Replica sets, elections, oplog, read preferences, write concerns, failover, arbiter nodes, hidden/delayed members | 🟡🔴 Intermediate-Advanced |
| 07 | [Sharding](./07_sharding.md) | Horizontal scaling, shard keys (hashed vs ranged), chunks, balancer, mongos, config servers, zones, resharding | 🔴 Advanced |
| 08 | [Performance & Production](./08_performance_and_production.md) | Connection pooling, profiler, slow queries, memory management, WiredTiger, security, backup/restore, monitoring, Atlas | 🔴 Advanced |
| 09 | [Interview Questions](./09_interview_questions.md) | 25+ categorized questions (beginner → advanced) + rapid-fire Q&A + system design with MongoDB | 🟢🟡🔴 All Levels |

## 🎯 Study Path

### Week 1: Foundations
1. Read `01_fundamentals.md` — understand the document model and CRUD
2. Practice queries using `mongosh` or [MongoDB Atlas free tier](https://www.mongodb.com/atlas)
3. Read `02_schema_design.md` — master embedding vs referencing trade-offs

### Week 2: Querying & Indexing
4. Read `03_indexing.md` — understand index types and `explain()` output
5. Read `04_aggregation.md` — build complex data pipelines
6. Read `05_transactions.md` — consistency guarantees and multi-doc transactions

### Week 3: Architecture & Operations
7. Read `06_replication.md` — replica set elections and failover
8. Read `07_sharding.md` — horizontal scaling strategies and shard key selection
9. Read `08_performance_and_production.md` — production configuration

### Final Review
10. Go through `09_interview_questions.md` — test yourself across all levels
