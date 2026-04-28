# Ingestion, Chunking, and Embeddings

## The Ingestion Side is Half the System

Many people over-focus on the LLM and under-focus on ingestion.

But in RAG, weak ingestion leads to weak retrieval, and weak retrieval leads to weak answers.

## Typical Ingestion Pipeline

```text
Source documents
  |
  v
Parse / clean text
  |
  v
Split into chunks
  |
  v
Generate embeddings
  |
  v
Store chunks + metadata + vectors
```

## Source Types

Common sources:

- PDFs
- Confluence / Notion docs
- support tickets
- code repositories
- SQL rows
- wiki pages
- runbooks

Each source may need different parsing and chunking treatment.

## Chunking

Chunking is one of the most important RAG design decisions.

Why:

- chunks too small lose context
- chunks too large add noise and token cost
- poor boundaries hurt retrieval precision

## Chunking Strategies

### 1. Fixed-size chunking

Split by tokens or characters.

Pros:

- simple
- predictable

Cons:

- may split ideas unnaturally

### 2. Recursive chunking

Try larger semantic boundaries first, then smaller ones if needed.

Often better for:

- markdown
- documentation
- long prose

### 3. Structure-aware chunking

Use:

- headings
- sections
- tables
- code blocks

This is often best for enterprise content.

## Overlap

Chunk overlap helps preserve continuity across boundaries.

Example:

- chunk size: 500 tokens
- overlap: 50 to 100 tokens

Too little overlap:

- context gets fragmented

Too much overlap:

- duplicates information
- increases storage and retrieval noise

## Metadata Design

Good metadata often matters as much as embeddings.

Useful fields:

- tenant ID
- document ID
- section title
- source type
- language
- timestamp
- access level
- version

This supports:

- filtering
- freshness control
- security
- auditability

## Embedding Model Choice

Choosing an embedding model is not trivial.

Consider:

- domain fit
- dimensionality
- cost
- latency
- multilingual support
- retrieval quality

Strong answer:

> I would choose the embedding model based on measured retrieval quality on my corpus, not only on benchmark popularity.

## Query and Document Embeddings

Many systems:

- embed documents offline
- embed user queries online

This means:

- query latency includes embedding time
- document freshness depends on re-embedding pipeline

## Freshness Problem

A common production failure:

- document updated
- stored chunks updated partially or not at all
- embeddings now stale

Fixes:

- document versioning
- re-embedding pipeline
- freshness monitoring

## Example Chunk Table Design

```sql
CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    document_id BIGINT NOT NULL,
    chunk_index INT NOT NULL,
    section_title TEXT,
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Example Ingestion Pseudocode

```python
def ingest_document(document):
    text = parse_document(document)
    chunks = split_into_chunks(text)

    rows = []
    for index, chunk in enumerate(chunks):
        vector = embedding_model.embed(chunk)
        rows.append({
            "document_id": document.id,
            "chunk_index": index,
            "content": chunk,
            "embedding": vector,
        })
    return rows
```

## Common Ingestion Mistakes

### 1. Ignoring structure

The system chunks raw text and loses headings, tables, or section context.

### 2. Chunking once and never revisiting it

Chunk strategy should be evaluated and iterated.

### 3. Embedding duplicates

Repeated identical or near-identical chunks pollute retrieval.

### 4. No document versioning

Stale chunks survive after source updates.

## Real-World Example: Policy Documents

Bad chunking:

- cuts policy clause in the middle
- strips heading and version number

Good chunking:

- keeps section header
- keeps clause boundary
- stores policy version metadata

This can dramatically improve retrieval reliability.

## MANG-Level Interview Insight

If asked "What matters most in RAG ingestion?" a strong answer is:

> Chunking and metadata design matter a lot. If chunks are misaligned with document structure or if filtering metadata is weak, retrieval quality suffers even with a strong embedding model. I would treat ingestion as a first-class system design problem, not as a preprocessing afterthought.

## Summary

Good RAG starts before retrieval.

If ingestion is weak, the rest of the system is fighting bad inputs.
