# Fundamentals and Mental Models

## What is RAG?

RAG stands for **Retrieval-Augmented Generation**.

Instead of asking the model to answer only from its internal weights, we:

1. retrieve relevant external context
2. place that context into the prompt
3. ask the model to answer using that context

## Why RAG Exists

LLMs have useful general knowledge, but they are weak for:

- fresh data
- private enterprise data
- domain-specific documents
- citation-heavy answers
- auditable answer generation

RAG addresses this by grounding generation in retrieved data.

## Core Problem RAG Solves

Suppose you build an enterprise assistant.

Users ask:

- "What is the current refund policy?"
- "Which internal service owns invoice reconciliation?"
- "What changed in the compliance doc last month?"

A base model may:

- answer from stale public knowledge
- hallucinate
- answer confidently without evidence

RAG improves this by retrieving relevant company documents first.

## Basic RAG Architecture

```text
Documents
  |
  v
Chunk and embed
  |
  v
Store in vector index / pgvector

User query
  |
  v
Embed query
  |
  v
Retrieve similar chunks
  |
  v
Prompt LLM with those chunks
  |
  v
Grounded answer
```

## Why RAG is Not "Just Search"

RAG has two major halves:

### Retrieval side

- ingestion
- chunking
- embeddings
- vector search
- filtering
- reranking

### Generation side

- prompt construction
- answer grounding
- abstention behavior
- citations
- structured output

If either half is weak, the system fails.

## RAG vs Fine-Tuning

This is one of the most common interview questions.

### RAG

Best for:

- dynamic knowledge
- enterprise documents
- fresh information
- traceable, source-grounded answers

### Fine-Tuning

Best for:

- output style
- repeated task behavior
- domain-specific formatting
- instruction following

Strong answer:

> RAG is usually the first choice when the problem is missing or changing knowledge. Fine-tuning is better when the problem is model behavior, format, or task adaptation. In production, many good systems use both: RAG for knowledge and fine-tuning for behavior.

## RAG vs Prompting Alone

Prompting alone is often enough if:

- the answer is generic
- the model already knows it
- there is no private knowledge dependency

RAG is needed when:

- correctness depends on external documents
- knowledge changes frequently
- you need citations or grounding

## When RAG Fails

RAG is helpful, but it is not magic.

Common failure reasons:

- bad chunking
- weak embeddings
- missing metadata filters
- wrong top-k
- no reranking
- prompt does not force grounding
- retrieved context is stale

## Typical RAG Use Cases

### 1. Enterprise document Q&A

Policies, contracts, docs, knowledge bases.

### 2. Support assistants

Combine policy docs, product docs, and past issue resolution content.

### 3. Developer assistants

Retrieve code, docs, incident notes, runbooks.

### 4. Research assistants

Retrieve evidence from reports, papers, and internal notes.

## Mental Model: Retriever is a Candidate Generator

Do not think:

- "retriever gives the answer"

Think:

- "retriever gives candidate evidence"

The LLM still has to:

- interpret context
- synthesize answer
- avoid unsupported claims

## Good RAG System Design Principles

- retrieve only from allowed data
- ground answers explicitly
- allow "I do not know"
- separate retrieval quality from answer quality
- evaluate both retrieval and generation

## Real-World Example

Suppose a policy assistant answers:

- "Refunds are allowed within 30 days."

To trust this, you want to know:

- which documents were retrieved
- whether they were current
- whether the answer quoted or cited the right sections

That is the value of RAG over free-form model memory.

## MANG-Level Interview Insight

If asked "What is RAG?" a strong answer is:

> RAG is a system design pattern where relevant external context is retrieved at inference time and supplied to the model so generation is grounded in fresh or private knowledge. It is especially useful when answers must depend on data that is too dynamic, too domain-specific, or too sensitive to encode reliably in model weights.

## Summary

RAG is not one trick.

It is a full system that combines:

- data pipelines
- retrieval
- prompting
- evaluation
- production operations
