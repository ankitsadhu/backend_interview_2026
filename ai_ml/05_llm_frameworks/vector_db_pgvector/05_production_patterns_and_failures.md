# Production Patterns and Failure Modes

## The Production Mindset

A demo proves vector search works once.

Production requires:

- retrieval quality
- freshness
- safe filtering
- predictable latency
- scalable ingestion
- observability

The biggest mistake is treating vector search as just "store embeddings and query top-k."

## Pattern 1: Version the Embedding Pipeline

Always track:

- embedding model name
- model version
- chunking strategy
- preprocessing logic

Why:

- changing any of these can alter retrieval quality
- mixed embeddings can create hard-to-debug results

## Pattern 2: Separate Retrieval Quality from LLM Quality

If users get bad answers, the issue may be:

- bad retrieval
- bad prompt grounding
- bad reranking
- bad generation

Do not blame the LLM first.

Measure retrieval separately using:

- recall@k
- hit rate on labeled answers
- citation correctness
- human feedback

## Pattern 3: Keep Ingestion Idempotent

If ingestion reruns, avoid duplicate rows.

Strategies:

- upserts
- version keys
- soft delete old versions
- unique constraints on content slices

## Pattern 4: Enforce Tenant and Access Filters

In enterprise systems, this is mandatory.

Vector search without strong filtering can cause:

- data leakage
- compliance issues
- broken trust

Strong answer in interviews:

> Vector relevance is useless if access control is wrong.

## Pattern 5: Use Hybrid Retrieval for Real Workloads

Pure semantic search often struggles with:

- IDs
- codes
- exact policy references
- abbreviations

Production systems often combine:

- vector retrieval
- keyword / BM25
- metadata filters
- reranking

## Pattern 6: Monitor Freshness

A common failure:

- source documents updated
- embeddings remain stale

Needed signals:

- document update lag
- embedding generation lag
- index refresh backlog
- percentage of stale chunks served

## Common Production Problems

### 1. Retrieval drift after embedding model change

Symptoms:

- quality drops after migration

Cause:

- new embeddings behave differently
- mixed old and new vectors

Fix:

- dual-write and compare
- backfill fully
- benchmark before cutover

### 2. Cross-tenant leakage

Symptoms:

- wrong customer data appears in results

Cause:

- missing mandatory filters

Fix:

- enforce filters at repository/query layer
- add tests specifically for isolation

### 3. Latency creep

Symptoms:

- top-k query acceptable in isolation
- end-to-end retrieval too slow

Cause:

- embedding generation latency
- ANN tuning too conservative
- heavy joins
- large reranking stage

### 4. Quality collapse from bad chunking

Symptoms:

- search returns vaguely related snippets

Cause:

- chunks too small or too large
- headers and context lost

Fix:

- redesign chunking
- keep structural context
- fetch neighboring chunks

### 5. Cost explosion

Symptoms:

- embedding bill rises sharply

Cause:

- too frequent re-embedding
- duplicate ingestion
- no delta update strategy

## When pgvector is Enough

This is a very good senior interview topic.

`pgvector` is often enough when:

- data size is moderate
- one-node or limited-scale deployment is acceptable
- metadata filtering is important
- team wants operational simplicity
- app already depends heavily on Postgres

## When to Consider a Dedicated Vector Database

Consider it when:

- vector corpus becomes very large
- latency requirements are very aggressive
- distributed ANN infrastructure is needed
- vector-heavy workloads outgrow the comfort zone of Postgres

But avoid premature migration.

Strong answer:

> I would start with `pgvector` if Postgres already exists in the stack and the workload is moderate, because the operational simplicity and relational filtering are strong advantages. I would move to a dedicated vector system only when scale, distribution, or performance requirements clearly justify the added operational complexity.

## Real-World Scenario: Enterprise RAG

Requirements:

- semantic retrieval over policy docs
- tenant isolation
- document freshness
- citations

Good design:

- chunk-level embeddings
- tenant-aware filtering
- ANN index for latency
- nightly evaluation suite
- stale-content monitoring

## Real-World Scenario: Support Ticket Search

Requirements:

- find similar historical tickets
- filter by product and region
- detect duplicates

Good design:

- vector retrieval for semantic similarity
- lexical path for ticket IDs
- hybrid search
- threshold-based near-duplicate checks

## What Interviewers Want to Hear

They want to see that you understand:

- vector search is only one piece of retrieval
- Postgres strengths are joins, filters, transactions, simplicity
- ANN always introduces tradeoffs
- freshness and access control matter as much as recall
- migration to a dedicated vector DB should be justified, not assumed

## Summary

Production vector search is about more than nearest neighbors.

The best systems are:

- well-modeled
- filtered
- benchmarked
- evaluated
- operationally simple for their scale
