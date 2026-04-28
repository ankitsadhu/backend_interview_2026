# LLM Frameworks and Systems

This folder covers practical LLM application engineering for interview preparation, from framework basics to production system design.

## Tracks

1. [LangChain](langchain/README.md) - chains, LCEL, retrievers, tools, agents, production patterns
2. [LangGraph](langgraph/README.md) - stateful workflows, graph execution, human-in-the-loop systems
3. [LangSmith](langsmith/README.md) - tracing, debugging, evaluations, observability
4. [Vector DB with pgvector](vector_db_pgvector/README.md) - vector search, indexes, similarity, production failures
5. [RAG Systems End to End](rag_systems_end_to_end/README.md) - ingestion, retrieval, reranking, generation, evaluation
6. [Fine-Tuning ML Models](fine_tuning_ml_models/README.md) - instruction tuning, LoRA, QLoRA, evaluation, deployment
7. [LLM Inference and Generation](llm_inference_and_generation/README.md) - quantization, KV cache, structured outputs, multimodal systems, serving

## Coverage Review

Strongly covered:

- RAG and vector search
- LangChain and LangGraph workflows
- tracing, evaluation, and debugging with LangSmith
- fine-tuning, LoRA, and QLoRA
- quantization and inference memory tradeoffs
- KV cache and context optimization
- structured outputs and function calling
- multimodal systems
- serving latency, batching, streaming, routing, and observability

Recommended future additions:

- LLM safety, prompt injection, and data exfiltration defenses
- prompt engineering and prompt evaluation patterns
- model selection and vendor abstraction strategies
- LLM system design case studies beyond RAG

## Interview Study Order

1. Start with LangChain fundamentals.
2. Learn vector search and RAG end to end.
3. Study structured outputs and tool calling.
4. Learn LangGraph for stateful and agentic workflows.
5. Study LangSmith evaluation and observability.
6. Learn fine-tuning, LoRA, and QLoRA.
7. Finish with inference optimization, multimodal systems, and production tradeoffs.

## MANG-Level Answer Pattern

For senior interview answers, always connect:

- first-principles mechanism
- coding or implementation shape
- tradeoffs
- failure modes
- evaluation and observability
- production rollout strategy

