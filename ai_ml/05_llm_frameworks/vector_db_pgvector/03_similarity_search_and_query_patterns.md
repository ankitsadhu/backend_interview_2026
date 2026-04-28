# Similarity Search and Query Patterns

## Basic Similarity Search

With `pgvector`, you search by comparing a query embedding to stored embeddings.

Typical flow:

1. embed the user query
2. compute similarity against stored vectors
3. return top-k nearest rows

## Important Operators

Common `pgvector` operators include:

- `<->` for L2 distance
- `<=>` for cosine distance
- `<#>` for negative inner product

Always verify which metric matches your embedding model and ranking goal.

## Basic Top-k Query

```sql
SELECT
    id,
    content,
    embedding <=> '[0.1, 0.2, 0.3]'::vector AS cosine_distance
FROM document_chunks
ORDER BY embedding <=> '[0.1, 0.2, 0.3]'::vector
LIMIT 5;
```

Smaller distance means more similar.

## Filtering + Similarity Search

This is one of the biggest practical advantages of using Postgres.

```sql
SELECT
    id,
    document_id,
    content
FROM document_chunks
WHERE tenant_id = 'acme'
ORDER BY embedding <=> '[0.1, 0.2, 0.3]'::vector
LIMIT 5;
```

This is critical in real systems:

- multitenancy
- language-specific search
- product-specific search
- document-type restrictions

## Metadata-Aware Query

```sql
SELECT
    dc.id,
    d.title,
    dc.content
FROM document_chunks dc
JOIN documents d ON d.id = dc.document_id
WHERE dc.tenant_id = 'acme'
  AND d.source_type = 'policy'
ORDER BY dc.embedding <=> '[0.1, 0.2, 0.3]'::vector
LIMIT 5;
```

This is why `pgvector` is attractive: vector search plus relational joins in one place.

## Query Pattern: Fetch Neighbor Chunks

A common RAG trick:

1. find a relevant chunk
2. also fetch nearby chunks for better context

```sql
WITH top_chunks AS (
    SELECT document_id, chunk_index
    FROM document_chunks
    WHERE tenant_id = 'acme'
    ORDER BY embedding <=> '[0.1, 0.2, 0.3]'::vector
    LIMIT 3
)
SELECT dc.*
FROM document_chunks dc
JOIN top_chunks tc
  ON dc.document_id = tc.document_id
 AND dc.chunk_index BETWEEN tc.chunk_index - 1 AND tc.chunk_index + 1;
```

This often improves answer quality because context continuity matters.

## Choosing `k`

Top-k is not just a tuning parameter. It directly affects:

- recall
- prompt size
- latency
- cost

### Small `k`

- faster
- cheaper
- may miss useful context

### Large `k`

- better recall
- more noise
- higher token usage

## Hybrid Search

Pure vector search is not always enough.

Why:

- exact identifiers matter
- legal clauses may require keyword precision
- SKU / invoice / ticket IDs are often lexical

Common solution:

- combine vector search with keyword search or BM25

## Simple Hybrid Search Pattern

Conceptually:

```text
vector candidates + keyword candidates -> merge / rerank -> final results
```

In Postgres, you can combine `pgvector` with:

- full-text search
- trigram search
- metadata filters

## Example: Full-Text + Vector Combination

```sql
SELECT
    id,
    content,
    ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', 'refund policy')) AS text_rank,
    embedding <=> '[0.1, 0.2, 0.3]'::vector AS vec_distance
FROM document_chunks
WHERE tenant_id = 'acme'
ORDER BY vec_distance ASC
LIMIT 10;
```

In practice, hybrid ranking often needs application-level fusion logic.

## Reranking

A common production pattern:

1. use vector search to get top 20 or top 50 candidates
2. rerank with a cross-encoder or LLM-aware reranker
3. send the best few results to the LLM

Why:

- first-stage retrieval optimizes speed
- reranking improves precision

## Query Pattern: Semantic Deduplication

Use vector search to find near duplicates:

```sql
SELECT
    id,
    content,
    embedding <=> '[0.1, 0.2, 0.3]'::vector AS distance
FROM document_chunks
WHERE tenant_id = 'acme'
  AND embedding <=> '[0.1, 0.2, 0.3]'::vector < 0.15
ORDER BY distance;
```

Threshold tuning is task-specific.

## Common Query Mistakes

### 1. No metadata filtering

Results become noisy or unsafe.

### 2. Too much context stuffed into the prompt

Latency and cost increase, answer quality may drop.

### 3. Wrong distance metric

The embedding model’s intended similarity behavior may not match the query.

### 4. Assuming nearest = correct

Top vector matches are candidates, not guarantees.

## Real-World Problems

### Problem: queries for invoice IDs perform badly

Cause:

- semantic search is weak for exact identifiers

Fix:

- hybrid search
- explicit metadata filtering
- lexical route for ID-like queries

### Problem: retrieved chunks are relevant but fragmented

Cause:

- chunking too small

Fix:

- fetch neighboring chunks
- change chunking strategy

### Problem: vector search returns right topic but wrong tenant

Cause:

- missing tenant filter

Fix:

- always filter by tenant before ranking

## MANG-Level Interview Insight

If asked "How would you design a vector retrieval query?" a strong answer is:

> I would not do pure nearest-neighbor search blindly. I would first apply mandatory filters like tenant, language, or document type, then run similarity search, and often fetch neighboring chunks or rerank the top candidates. In production, retrieval quality comes from the full query strategy, not just from storing embeddings.

## Summary

Strong vector retrieval is usually:

- filtered
- top-k tuned
- sometimes hybrid
- often reranked
- evaluated on real workloads
