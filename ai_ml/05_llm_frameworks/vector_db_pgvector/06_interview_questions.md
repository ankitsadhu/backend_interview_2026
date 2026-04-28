# Interview Questions

## 1. What is a vector database?

A vector database stores embeddings and supports similarity search over them so that semantically similar items can be retrieved efficiently.

## 2. What is an embedding?

An embedding is a dense numeric vector representation of data such as text or images, where semantically similar items are closer in vector space.

## 3. What is `pgvector`?

`pgvector` is a PostgreSQL extension that adds vector storage and similarity search capabilities to Postgres.

## 4. Why use `pgvector` instead of a dedicated vector database?

Because it lets you keep embeddings alongside relational data in PostgreSQL, use SQL and joins, apply strong metadata filters, and avoid introducing another system too early.

## 5. When would you not use `pgvector`?

I would reconsider it when the vector workload becomes very large, distributed, or extremely latency-sensitive, and Postgres no longer provides the best operational or performance fit.

## 6. What distance metrics are commonly used in vector search?

- cosine similarity / cosine distance
- Euclidean distance (L2)
- inner product

## 7. Which metric should you choose for text embeddings?

Often cosine similarity is a good default for text embeddings, but the correct choice depends on the embedding model and how it was trained. I would follow model guidance and validate retrieval quality empirically.

## 8. What is the difference between exact and approximate nearest-neighbor search?

- exact search compares against all candidates and is more accurate
- approximate search uses indexing structures to trade some recall for better speed

## 9. What ANN index types should you know in `pgvector`?

- IVFFlat
- HNSW

## 10. What is the tradeoff when using ANN indexes?

The main tradeoff is recall versus latency. Faster search may miss some of the true nearest neighbors.

## 11. What is top-k in vector retrieval?

Top-k is the number of nearest results returned for a query. It affects recall, prompt size, latency, and cost.

## 12. Why is chunking important in RAG with `pgvector`?

Because embeddings are usually stored at chunk level, and chunk size strongly affects retrieval quality. Chunks that are too small lose context, while chunks that are too large add noise and cost.

## 13. Why is metadata filtering important?

Because retrieval should be constrained by tenant, language, access policy, product, or document type. In production, filtering is essential for relevance and security.

## 14. What is hybrid search?

Hybrid search combines vector similarity with lexical or keyword search. It is useful because exact identifiers and codes often perform poorly with pure semantic retrieval.

## 15. Why might retrieval quality be poor even with a strong model?

- bad chunking
- wrong embedding model
- stale embeddings
- poor filters
- weak top-k choice
- lack of reranking

## 16. How would you design a `pgvector` schema for RAG?

I would usually store embeddings at chunk level, keep strong relational fields like `document_id` and `tenant_id`, track the embedding model version, and use metadata selectively rather than placing everything into one JSON blob.

## 17. What should you monitor in production?

- retrieval latency
- recall or retrieval hit rate
- stale embedding lag
- index build / refresh lag
- cross-tenant leakage risk
- token cost from retrieved context

## 18. How would you decide between `pgvector` and a dedicated vector DB?

I would start with `pgvector` if the team already uses Postgres and the workload is moderate, especially when relational filtering matters. I would move to a dedicated vector DB only when the scale or performance needs clearly justify the added complexity.

## Rapid-Fire Answers

### Is vector search enough by itself for production RAG?

No. You also need filtering, chunking, reranking, evaluation, and prompt grounding.

### Does nearest neighbor always mean best answer?

No. It means best candidate under the similarity metric, not guaranteed correctness.

### Should you mix embeddings from different models in one column casually?

No. That can cause inconsistent search behavior and makes evaluation harder.

### Is Postgres filtering a strength of `pgvector`?

Yes. It is one of the biggest reasons to use it.

### What is the most common production risk?

Weak retrieval design, especially stale data and missing access-control filters.

## Final Interview Tip

For vector database interviews, always connect:

1. embedding fundamentals
2. retrieval quality
3. indexing tradeoffs
4. production filtering and freshness

That combination makes the answer sound strong and practical instead of superficial.
