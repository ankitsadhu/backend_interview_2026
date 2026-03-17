# PostgreSQL Study Guide

> Comprehensive PostgreSQL learning path from beginner to advanced, organized for interview preparation.

## 📁 Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | Architecture, processes, memory, data types, basic CRUD, constraints, schemas | 🟢 Beginner |
| 02 | [Indexing](./02_indexing.md) | B-Tree, Hash, GIN, GiST, BRIN, partial indexes, composite indexes, covering indexes, index-only scans | 🟢🟡 Beginner-Intermediate |
| 03 | [Query Optimization](./03_query_optimization.md) | EXPLAIN/ANALYZE, query planner, scan types, join algorithms, statistics, common pitfalls | 🟡 Intermediate |
| 04 | [Joins — Deep Dive](./04_joins.md) | INNER, LEFT, RIGHT, FULL OUTER, CROSS, self joins, LATERAL, anti-joins, semi-joins, join algorithms | 🟢🟡 Beginner-Intermediate |
| 05 | [Transactions & Concurrency](./04_transactions_and_concurrency.md) | ACID, isolation levels, MVCC, row-level locking, advisory locks, deadlocks, VACUUM | 🟡 Intermediate |
| 06 | [Advanced SQL](./05_advanced_sql.md) | CTEs, window functions, LATERAL joins, JSON/JSONB, arrays, full-text search, recursive queries | 🟡🔴 Intermediate-Advanced |
| 07 | [Partitioning & Sharding](./06_partitioning_and_sharding.md) | Declarative partitioning, range/list/hash, partition pruning, Citus, sharding strategies | 🟡🔴 Intermediate-Advanced |
| 08 | [Replication & HA](./07_replication_and_ha.md) | Streaming replication, logical replication, WAL, failover, Patroni, pg_basebackup | 🔴 Advanced |
| 09 | [Performance & Production](./08_performance_and_production.md) | Connection pooling (PgBouncer), memory tuning, autovacuum, monitoring, security, backups | 🔴 Advanced |
| 10 | [Interview Questions](./09_interview_questions.md) | 25+ categorized questions (beginner → advanced) + rapid-fire Q&A + system design | 🟢🟡🔴 All Levels |

## 🎯 Study Path

### Week 1: Foundations
1. Read `01_fundamentals.md` — understand PostgreSQL architecture and data types
2. Practice SQL using `psql` or any local PostgreSQL instance
3. Read `02_indexing.md` — understand index types and when to use each

### Week 2: Queries & Transactions
4. Read `03_query_optimization.md` — master EXPLAIN and query tuning
5. Read `04_joins.md` — deep dive into all join types and algorithms
6. Read `04_transactions_and_concurrency.md` — understand MVCC and isolation levels
7. Read `05_advanced_sql.md` — window functions, CTEs, JSON

### Week 3: Scale & Production
7. Read `06_partitioning_and_sharding.md` — partitioning strategies
8. Read `07_replication_and_ha.md` — replication and high availability
9. Read `08_performance_and_production.md` — production tuning and monitoring

### Final Review
10. Go through `09_interview_questions.md` — test yourself across all levels
