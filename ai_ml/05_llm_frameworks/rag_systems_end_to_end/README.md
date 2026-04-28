# RAG Systems End-to-End Learning Path

This track focuses on **Retrieval-Augmented Generation (RAG) systems end to end**.

It is designed for interview preparation from basic to advanced, with emphasis on:

- RAG fundamentals and architecture
- ingestion, chunking, embeddings, and retrieval
- `pgvector`-backed storage patterns
- orchestration with LangChain and LangGraph
- evaluation with LangSmith-style thinking
- production tradeoffs and real-world failure modes

## Contents

1. [Fundamentals and Mental Models](01_fundamentals_and_mental_models.md) - what RAG is, when to use it, core architecture
2. [Ingestion, Chunking, and Embeddings](02_ingestion_chunking_and_embeddings.md) - loaders, chunk design, embedding strategy, freshness
3. [Retrieval, Ranking, and Query Pipelines](03_retrieval_ranking_and_query_pipelines.md) - top-k, filtering, hybrid search, reranking, neighbor chunks
4. [Building RAG with pgvector and LangChain](04_building_rag_with_pgvector_and_langchain.md) - practical schema, retrieval queries, chain examples
5. [Advanced RAG with LangGraph and Agents](05_advanced_rag_with_langgraph_and_agents.md) - iterative retrieval, validation loops, tool use, human checkpoints
6. [Evaluation, Observability, and Production](06_evaluation_observability_and_production.md) - offline evals, traces, latency, cost, failures
7. [Interview Questions](07_interview_questions.md) - MANG-style questions with concise answers

## How to Study

Recommended order:

1. Understand what problem RAG actually solves.
2. Learn why chunking and retrieval quality matter as much as the model.
3. Learn how to implement a baseline RAG stack with Postgres + `pgvector`.
4. Study advanced orchestration only after the baseline is clear.
5. Finish with evaluation and production readiness.

## Mental Model

```text
User Query
  |
  v
Embed query
  |
  v
Retrieve relevant context
  |
  v
Optional rerank / validate
  |
  v
Prompt LLM with grounded context
  |
  v
Answer with citations / structured output
```

## Why RAG Matters in Interviews

Many candidates say:

- "Use RAG for knowledge."

Fewer can explain:

- when RAG is better than fine-tuning
- how chunking affects retrieval quality
- why metadata filtering is mandatory
- how hybrid search improves results
- how to evaluate retrieval separately from generation
- how to debug hallucinations in production

That is where strong interview performance stands out.
