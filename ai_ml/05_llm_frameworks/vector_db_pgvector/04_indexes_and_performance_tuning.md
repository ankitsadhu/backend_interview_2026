# Indexes and Performance Tuning

## Exact Search vs Indexed Search

Without a vector index, PostgreSQL does exact nearest-neighbor search by scanning many rows.

This can be fine for:

- small datasets
- prototyping
- evaluation baselines

But it becomes slow as the dataset grows.

## Why Approximate Indexing Exists

Approximate nearest-neighbor indexing improves latency by avoiding full comparisons across all rows.

Tradeoff:

- much faster queries
- slightly lower recall

This recall-latency tradeoff is one of the most important interview topics.

## pgvector Index Types

The main approximate index types you should know:

- IVFFlat
- HNSW

## IVFFlat

IVFFlat groups vectors into clusters and searches only selected clusters.

Think of it like:

```text
all vectors
  -> partition into lists / clusters
  -> query probes relevant clusters
  -> rank candidates within them
```

### Create IVFFlat index

```sql
CREATE INDEX idx_chunks_embedding_ivfflat
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

Operator class depends on the metric:

- `vector_l2_ops`
- `vector_ip_ops`
- `vector_cosine_ops`

### IVFFlat tuning

Important setting:

- `lists`

More lists:

- better recall potential
- larger index
- may need more probes

### Query-time tuning

```sql
SET ivfflat.probes = 10;
```

Higher probes:

- better recall
- higher latency

## HNSW

HNSW stands for **Hierarchical Navigable Small World**.

It is a graph-based ANN structure and often gives strong recall-latency tradeoffs.

### Create HNSW index

```sql
CREATE INDEX idx_chunks_embedding_hnsw
ON document_chunks
USING hnsw (embedding vector_cosine_ops);
```

### Why HNSW is popular

- good recall
- strong latency characteristics
- often better query performance than simpler ANN methods

But:

- indexing can be heavier
- memory usage can matter more

## How to Choose Between IVFFlat and HNSW

### IVFFlat

Good when:

- you want simpler ANN indexing
- you can tune lists/probes carefully
- workload is moderate

### HNSW

Good when:

- you want stronger recall-latency performance
- you can afford more complex indexing cost

## Measure, Do Not Guess

A strong engineering habit:

- compare exact baseline vs ANN
- measure recall@k
- measure p50 / p95 latency
- measure index build cost

Do not tune only for speed if retrieval quality matters.

## Example Benchmark Mindset

For a RAG workload, compare:

1. exact search
2. IVFFlat with different `lists` and `probes`
3. HNSW

Track:

- recall@5
- recall@10
- latency
- memory
- build time

## Filtering and Planner Behavior

A common interview trap:

Vector index performance is not only about the vector index.

Why:

- tenant filters matter
- joins matter
- additional predicates matter
- row counts matter

If a query has heavy filtering, sometimes query shape or schema design matters more than raw ANN tuning.

## Supporting Relational Indexes

Do not forget normal Postgres indexes.

Examples:

```sql
CREATE INDEX idx_chunks_tenant_id ON document_chunks (tenant_id);
CREATE INDEX idx_chunks_document_id_chunk_index ON document_chunks (document_id, chunk_index);
CREATE INDEX idx_documents_source_type ON documents (source_type);
```

These are critical when vector search is combined with filters and joins.

## Table Growth and Maintenance

As embeddings grow:

- table size increases
- index build times increase
- vacuum and autovacuum matter
- bloat can hurt performance

Remember: `pgvector` lives inside Postgres, so normal Postgres operational concerns still apply.

## Partitioning

At larger scale, partitioning may help.

Useful partition keys:

- tenant
- time
- dataset

Benefits:

- smaller active working sets
- better isolation
- operational flexibility

But partitioning adds complexity and should be justified by workload.

## Common Performance Problems

### 1. Exact scan on a huge table

Cause:

- no vector index

### 2. Low recall after adding ANN index

Cause:

- poor ANN tuning
- wrong operator class
- too few probes / weak index config

### 3. Good ANN latency but bad end-to-end RAG latency

Cause:

- query embedding generation dominates
- reranking dominates
- LLM prompt size dominates

### 4. Good vector index, poor filtered search

Cause:

- missing B-tree indexes on filters
- poor query shape

## Practical Tuning Advice

### Start with exact search

Why:

- gives quality baseline
- helps verify query correctness

### Then add ANN

Why:

- now you can quantify speed vs recall loss

### Benchmark on production-like traffic

Why:

- synthetic tests may hide real tenant/filter distributions

## MANG-Level Interview Insight

If asked "How would you tune `pgvector`?" a strong answer is:

> I would start with exact search to establish the recall baseline, then introduce ANN indexing such as IVFFlat or HNSW and measure recall-latency tradeoffs on real queries. I would not tune the vector index in isolation; I would also optimize metadata filters, relational indexes, query shape, and end-to-end RAG latency, because the vector lookup is only one part of retrieval performance.

## Summary

Performance tuning for `pgvector` is about:

- the right metric
- the right ANN index
- the right filters
- the right benchmarks
- the right quality-speed tradeoff
