# Vector Databases with pgvector Learning Path

This track focuses on **vector search using PostgreSQL + pgvector**.

It is designed for interview preparation from basic to advanced, with emphasis on:

- embeddings and similarity search fundamentals
- schema design in PostgreSQL
- `pgvector` operators and indexes
- hybrid search and RAG use cases
- performance and production tradeoffs
- MANG-style interview questions

## Contents

1. [Fundamentals](01_fundamentals.md) - embeddings, vector search basics, why pgvector exists
2. [pgvector Setup and Data Modeling](02_pgvector_setup_and_data_modeling.md) - extension setup, schema patterns, ingestion
3. [Similarity Search and Query Patterns](03_similarity_search_and_query_patterns.md) - distance metrics, top-k search, filtering, hybrid search
4. [Indexes and Performance Tuning](04_indexes_and_performance_tuning.md) - IVFFlat, HNSW, recall/latency tradeoffs, query planning
5. [Production Patterns and Failure Modes](05_production_patterns_and_failures.md) - scaling, freshness, multitenancy, cost, reliability
6. [Interview Questions](06_interview_questions.md) - MANG-style questions with concise answers

## How to Study

Recommended order:

1. Understand embeddings and vector similarity first.
2. Learn how `pgvector` stores vectors in PostgreSQL.
3. Practice query patterns for top-k retrieval and filtering.
4. Learn approximate indexing and tuning tradeoffs.
5. Finish with production scenarios and interview questions.

## Mental Model

```text
Raw Data
  |
  v
Chunk / preprocess text
  |
  v
Embedding model
  |
  v
Store vectors in PostgreSQL (pgvector)
  |
  v
Similarity search + metadata filters
  |
  v
Retrieved context for RAG / search / recommendations
```

## Why pgvector Matters in Interviews

Many candidates can say "use a vector DB for RAG."

Fewer can explain:

- what a vector actually represents
- cosine vs inner product vs L2 distance
- when `pgvector` is good enough
- how approximate indexes work
- how filtering interacts with vector search
- when to move from Postgres to a dedicated vector store

That is where strong interview performance stands out.
