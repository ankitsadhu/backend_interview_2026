# Retrieval, Ranking, and Query Pipelines

## Retrieval is More Than Top-k Search

A strong RAG system does not just:

- embed query
- fetch nearest chunks
- stop thinking

Real retrieval pipelines often include:

- filters
- hybrid search
- neighboring context
- reranking
- query rewriting

## Baseline Query Pipeline

```text
User query
  |
  v
Embed query
  |
  v
Vector retrieval
  |
  v
Prompt LLM with top-k chunks
```

This is a fine baseline, but often not enough for production.

## Metadata Filtering

Mandatory filters may include:

- tenant
- language
- document type
- permissions
- freshness window

Strong answer:

> In production, retrieval should first be safe and relevant before it is clever.

## Top-k Tradeoff

Choosing `k` affects:

- recall
- prompt size
- latency
- cost
- noise

### Small `k`

- cheaper
- faster
- may miss useful evidence

### Large `k`

- better recall
- more irrelevant context
- more expensive generation

## Fetching Neighbor Chunks

A common improvement:

1. retrieve a chunk
2. also fetch chunk before and after it

Why:

- semantic match may hit one sentence
- answer often needs surrounding context

## Hybrid Search

Pure vector search can fail on:

- invoice numbers
- API names
- exact policy clause references
- error codes

Hybrid search combines:

- semantic similarity
- lexical matching

This is often superior in enterprise search.

## Reranking

A common modern pipeline:

1. retrieve top 20 to 50 chunks fast
2. rerank for precision
3. send only best few chunks to the model

Reranking is useful because:

- first-stage retrieval optimizes recall and speed
- reranking optimizes final quality

## Query Rewriting

Sometimes the user query is too vague or noisy.

Examples:

- pronoun-heavy follow-up
- short ambiguous query
- multi-part request

A query rewrite step can improve retrieval.

But be careful:

- rewriting can distort user intent
- it adds latency

## Example pgvector Query Pattern

```sql
SELECT
    id,
    content
FROM document_chunks
WHERE tenant_id = 'acme'
  AND updated_at > now() - interval '180 days'
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

This illustrates an important idea:

- vector similarity + mandatory filters

## Retrieval Failure Modes

### 1. Right topic, wrong document

Cause:

- coarse chunking
- weak reranking

### 2. Right document, wrong tenant

Cause:

- missing tenant filter

### 3. Right document, bad answer

Cause:

- prompt did not enforce grounding
- too much noisy context

### 4. Empty retrieval for obvious query

Cause:

- bad embeddings
- stale index
- wrong metadata filters

## Query Pipeline Patterns

### 1. Basic semantic retrieval

Good first baseline.

### 2. Filtered retrieval

Needed for real enterprise systems.

### 3. Hybrid retrieval

Needed when exact terms matter.

### 4. Retrieve + rerank

Needed when precision is critical.

### 5. Iterative retrieval

Useful in complex or multi-hop workflows.

## Real-World Example: Support Assistant

User asks:

- "Can I refund order 18273 if it shipped already?"

A strong retrieval pipeline may:

1. detect order-like identifier
2. hit order tool or metadata route
3. retrieve refund policy docs
4. rerank policy passages
5. pass both structured order state and policy evidence to the LLM

This is much better than generic semantic retrieval alone.

## MANG-Level Interview Insight

If asked "How do you improve retrieval quality?" a strong answer is:

> I would not focus only on the embedding model. I would improve chunking, apply strong metadata filters, tune top-k, add hybrid search where exact tokens matter, and rerank candidates before generation. Retrieval quality usually comes from the full pipeline design rather than one isolated component.

## Summary

Strong retrieval pipelines are usually:

- filtered
- staged
- sometimes hybrid
- often reranked
- carefully tuned to the workload
