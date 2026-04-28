# Interview Questions

## 1. What is RAG?

RAG is a system pattern where relevant external context is retrieved at inference time and supplied to the model so that the answer is grounded in fresh, private, or domain-specific knowledge.

## 2. Why use RAG instead of only fine-tuning?

Because fine-tuning is not a good solution for dynamic or frequently changing knowledge. RAG is better when answers need fresh external data or citations.

## 3. When would you combine RAG and fine-tuning?

I would use RAG for knowledge grounding and fine-tuning for behavior, structure, tone, or domain-specific output patterns.

## 4. What are the main parts of a RAG system?

- ingestion
- chunking
- embeddings
- storage / vector index
- retrieval
- optional reranking
- prompt construction
- grounded generation
- evaluation and monitoring

## 5. Why is chunking important?

Because chunk size and boundaries strongly affect retrieval quality. Chunks that are too small lose context, while chunks that are too large add noise and cost.

## 6. Why is metadata filtering important?

Because real systems need tenant isolation, permissions, language constraints, source filtering, and freshness control. Vector similarity alone is not enough.

## 7. What is hybrid search?

Hybrid search combines semantic retrieval with lexical or keyword retrieval. It is useful when exact identifiers, codes, or legal phrases matter.

## 8. What is reranking and why use it?

Reranking means retrieving a broader candidate set first, then using a stronger ranking step to improve final precision before generation.

## 9. Does RAG eliminate hallucinations?

No. It reduces hallucinations by grounding answers in retrieved context, but failures still happen if retrieval is poor, context is noisy, or the prompt does not enforce grounded answering.

## 10. How would you evaluate a RAG system?

I would evaluate retrieval and generation separately. For retrieval, I would look at recall@k and evidence quality. For generation, I would measure groundedness, correctness, abstention behavior, citations, latency, and cost.

## 11. What are common RAG failure modes?

- bad chunking
- stale embeddings
- weak metadata filtering
- poor top-k choice
- missing reranking
- unsupported generation despite good context
- cross-tenant leakage

## 12. How would you build a simple production-minded RAG system?

I would ingest and chunk documents carefully, store embeddings and metadata in a vector store like `pgvector`, retrieve with strong filters, prompt the model to answer only from context or abstain, and then evaluate the baseline before adding more complexity.

## 13. When should you use LangGraph in RAG?

When the workflow becomes stateful or non-linear, such as iterative retrieval, tool calls, validation loops, or human approval steps.

## 14. When should you avoid over-engineering RAG?

When a simple retrieval-plus-prompt baseline already solves the problem. Many systems do not need agentic or graph-based orchestration.

## 15. What is the strongest one-line explanation of RAG?

RAG grounds model generation in retrieved external evidence at inference time so answers can reflect current, private, or domain-specific knowledge.

## Rapid-Fire Answers

### Is vector search enough by itself?

No. You also need chunking, filtering, prompting, and evaluation.

### What matters more, the model or retrieval?

Both matter, but poor retrieval can break even a strong model.

### Should every RAG system use reranking?

No. Start with a baseline and add reranking only if precision needs improvement.

### What is the biggest security risk in RAG?

Improper access-control or tenant filtering.

### What is the biggest product risk in RAG?

Confident but unsupported answers.

## Final Interview Tip

For RAG interviews, always connect:

1. ingestion quality
2. retrieval design
3. grounded generation
4. evaluation and production operations

That makes the answer sound senior, practical, and end-to-end.
