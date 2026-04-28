# LangChain Learning Path

LangChain is a framework for building LLM-powered applications using reusable abstractions such as prompts, models, parsers, retrievers, tools, chains, and agents.

This track is designed for interview preparation from basic to advanced, with emphasis on:

- clear fundamentals
- code examples
- RAG and agent use cases
- production tradeoffs
- real-world failure modes
- interview-style questions and answers

## Contents

1. [Fundamentals](01_fundamentals.md) - what LangChain is, why it exists, core building blocks
2. [Core Components and LCEL](02_core_components_and_lcel.md) - prompts, models, output parsers, runnables, composition
3. [Chains, RAG, and Retrieval](03_chains_rag_and_retrieval.md) - document pipelines, retrievers, chunking, retrieval patterns
4. [Agents and Tool Calling](04_agents_and_tool_calling.md) - tool orchestration, planning, routing, common pitfalls
5. [Production Patterns and Failure Modes](05_production_patterns_and_failures.md) - scaling, debugging, latency, cost, reliability
6. [Interview Questions](06_interview_questions.md) - MANG-style questions with concise answers

## How to Study

Recommended order:

1. Learn the problem LangChain is trying to solve.
2. Understand LCEL and the core building blocks deeply.
3. Learn chains and RAG before jumping into agents.
4. Study agents only after you understand tool calling and failure handling.
5. Finish with production tradeoffs and interview questions.

## Mental Model

```text
User Request
   |
   v
LangChain Application
   |
   +--> Prompt templates
   +--> LLM / chat models
   +--> Retrievers / vector stores
   +--> Tools / external APIs
   +--> Output parsers
   +--> Chains / agents
   |
   v
Answer / Action
```

## Why LangChain Matters in Interviews

Many candidates know how to call an LLM API once.

Fewer can explain:

- how to structure multi-step LLM workflows
- how to build RAG cleanly
- how tools and agents should be controlled
- how to compose steps without creating spaghetti code
- when LangChain helps and when custom code is better

That is where LangChain becomes valuable.
