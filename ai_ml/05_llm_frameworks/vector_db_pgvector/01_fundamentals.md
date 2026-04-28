# Fundamentals

## What is a Vector Database?

A vector database stores and searches **embeddings** efficiently.

An embedding is a numeric representation of data such that semantically similar items are close in vector space.

Examples:

- similar questions
- similar documents
- similar images
- similar products

## What is an Embedding?

An embedding is usually a high-dimensional array of floating-point numbers.

Example:

```text
"How do I reset my password?"
-> [0.12, -0.44, 0.91, ..., 0.07]
```

The exact numbers are not human-interpretable, but geometry matters:

- semantically similar text -> vectors closer together
- unrelated text -> vectors farther apart

## Why Vector Search Matters

Traditional search is often lexical:

- exact term match
- keyword scoring
- BM25

Vector search enables semantic retrieval:

- "change password" can match "reset login credentials"
- "delivery issue" can match "shipment delayed"

This is why vector search is popular for:

- RAG
- semantic search
- recommendations
- duplicate detection
- support knowledge retrieval

## Where pgvector Fits

`pgvector` is a PostgreSQL extension that adds a vector data type and similarity operators.

This lets you use PostgreSQL for:

- storing embeddings
- similarity search
- metadata filtering
- transactional writes
- combining vector and relational data

## Why Use PostgreSQL + pgvector?

Because many teams already use Postgres.

Benefits:

- one database for app data and embeddings
- SQL support
- joins with relational data
- transactions
- simpler operations for small and medium workloads

## When pgvector is a Good Fit

`pgvector` is a strong choice when:

- your team already uses PostgreSQL
- the scale is moderate
- you need strong metadata filtering
- you want transactional consistency
- operational simplicity matters

## When pgvector May Not Be Enough

At very large scale or extreme low-latency requirements, dedicated vector databases may be better.

Typical pressure points:

- huge embedding collections
- high write throughput
- distributed vector serving
- advanced ANN tuning / sharding needs

## Distance Metrics

This is an interview favorite.

### 1. Cosine similarity

Measures angle similarity between vectors.

Good when vector magnitude matters less than direction.

Common for text embeddings.

### 2. Euclidean distance (L2)

Measures straight-line distance between vectors.

Useful when absolute geometry matters.

### 3. Inner product

Measures similarity via dot product.

Often used when embeddings are normalized or model-specific guidance recommends it.

## Intuition for Similarity

```text
Question embedding
   |
   +--> nearest neighbors:
         - FAQ chunk 12
         - Help article 7
         - Ticket summary 202
```

Instead of exact string matching, we search by closeness in vector space.

## Exact vs Approximate Nearest Neighbor Search

### Exact search

Compares against all candidates.

Pros:

- accurate
- simple

Cons:

- slower at scale

### Approximate nearest neighbor (ANN)

Uses indexing structures to trade a bit of recall for much better speed.

Pros:

- faster
- scalable

Cons:

- may miss some true nearest neighbors

## Why This Matters in RAG

RAG often works like this:

1. chunk documents
2. generate embeddings
3. store embeddings
4. retrieve top-k similar chunks for a user query
5. send retrieved context to the LLM

If retrieval quality is bad, even a strong LLM can answer poorly.

## Basic pgvector Example

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536)
);
```

The dimension should match the embedding model output size.

## Typical Use Cases

### 1. RAG document retrieval

Retrieve relevant chunks for a question-answering system.

### 2. Semantic search

Search support tickets, internal docs, policies, or knowledge base articles.

### 3. Recommendations

Find similar products, users, or items.

### 4. Duplicate / near-duplicate detection

Find repeated tickets, articles, or bug reports.

## Common Misconceptions

### "Vector DB means only one kind of search"

No. Real systems often combine:

- vector search
- metadata filters
- keyword search
- reranking

### "Embeddings remove the need for schema design"

No. You still need good tables, indexes, filters, and document metadata.

### "If I add vectors, retrieval quality is solved"

No. Quality also depends on:

- chunking
- embedding model quality
- metadata filters
- top-k choice
- reranking

## MANG-Level Interview Insight

If asked "What is `pgvector`?" a strong answer is:

> `pgvector` is a PostgreSQL extension that adds vector storage and similarity search to Postgres. It allows embeddings to be stored alongside relational data and queried using metrics like cosine distance, inner product, or L2 distance. It is especially useful when you want semantic search or RAG without introducing a separate vector database too early.

## Summary

The core idea is simple:

- embeddings turn meaning into vectors
- vector search retrieves semantically similar items
- `pgvector` brings that capability into PostgreSQL
