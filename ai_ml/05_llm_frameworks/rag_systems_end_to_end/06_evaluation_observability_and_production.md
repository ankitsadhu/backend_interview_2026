# Evaluation, Observability, and Production

## Why RAG Needs Separate Evaluation

RAG quality is not just "Did the answer sound good?"

You must evaluate:

- retrieval quality
- grounding quality
- final answer quality
- latency
- cost

A good answer can still be dangerously unsupported.

## What to Measure

### Retrieval metrics

- recall@k
- precision@k
- hit rate
- citation coverage

### Generation metrics

- correctness
- groundedness
- completeness
- abstain quality
- format compliance

### System metrics

- p50 / p95 latency
- token cost
- retrieval latency
- reranker latency
- error rate

## Retrieval vs Generation Failures

A strong candidate separates them clearly.

### Retrieval failure

- wrong or missing context fetched

### Generation failure

- right context fetched, but answer is wrong or unsupported

This distinction is essential for debugging.

## Offline Evaluation

Build a dataset of:

- real queries
- hard failure cases
- ambiguous queries
- long-context questions
- exact-ID queries
- no-answer queries

Useful checks:

- did retrieval bring the right evidence?
- did final answer cite the right chunk?
- did model abstain when context was missing?

## Online Evaluation

Track:

- user feedback
- escalation rate
- citation click-through or usage
- correction rate
- latency by query type

## Observability

A production RAG system should trace:

- user query
- rewritten query if any
- retrieved chunk IDs
- scores or ranking order
- prompt version
- model version
- final answer

This makes debugging possible.

## Common Production Problems

### 1. Hallucinations despite retrieval

Cause:

- prompt did not enforce grounding
- retrieved context weak or noisy
- no abstain behavior

### 2. Stale documents

Cause:

- ingestion pipeline lag
- missing re-embedding

### 3. Cross-tenant leakage

Cause:

- weak metadata filtering

### 4. Good retrieval, bad answer

Cause:

- answer synthesis prompt weak
- too much context passed

### 5. Good answer, terrible latency

Cause:

- expensive query embedding
- slow vector search
- reranker too heavy
- too many chunks passed to the model

## Practical Dashboards

Useful slices:

- tenant
- source type
- prompt version
- retriever version
- chunk strategy version
- query category

This helps localize regressions faster.

## Production RAG Playbook

When quality drops:

1. inspect failing traces
2. determine retrieval vs generation failure
3. check document freshness
4. compare chunking / retriever versions
5. rerun offline evals on failure set
6. roll back if needed

## Cost Control

RAG cost comes from:

- document embedding
- query embedding
- retrieval
- reranking
- LLM context size

Mitigations:

- trim `k`
- use better reranking
- compress context
- cache embeddings
- use cheaper models for intermediate steps

## Safe Deployment Pattern

Use:

- baseline before optimization
- regression datasets
- canary rollouts
- prompt versioning
- retriever versioning
- index versioning

Strong answer:

> In RAG, changing chunking or retriever logic can be as impactful as changing the model, so those changes should be versioned and evaluated like code.

## Real-World Scenario: Enterprise Policy Assistant

Important signals:

- stale policy hit rate
- missing citation rate
- unsupported answer rate
- policy version drift

## Real-World Scenario: Support Copilot

Important signals:

- ticket deflection rate
- escalation rate
- answer acceptance rate
- policy retrieval accuracy

## MANG-Level Interview Insight

If asked "How do you make RAG production-ready?" a strong answer is:

> I would separate retrieval and generation evaluation, trace the full pipeline, enforce strong metadata filtering, version ingestion and retrieval components, and monitor freshness, latency, and groundedness together. Production RAG is not just a prompt with a vector store; it is a retrieval system plus an answer-generation system plus an operations problem.

## Summary

Production RAG is about:

- evidence quality
- traceability
- measurable performance
- safe iteration
