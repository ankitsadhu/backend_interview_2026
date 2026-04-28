# pgvector Setup and Data Modeling

## Installing pgvector

On PostgreSQL, enable the extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

After that, you can use the `VECTOR(n)` type.

## Basic Schema

```sql
CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ DEFAULT now()
);
```

This is a common RAG-oriented schema.

## Why Chunk-Level Storage?

Store embeddings at **chunk level**, not always full-document level.

Why:

- retrieval needs finer granularity
- smaller chunks reduce irrelevant context
- one large document may contain many topics

## Important Columns

### `document_id`

Lets you map chunks back to the parent document.

### `chunk_index`

Useful for:

- reconstructing context windows
- fetching neighboring chunks

### `metadata`

Useful for:

- tenant ID
- document type
- language
- source URL
- created date
- access control labels

### `embedding`

Stores the numeric vector. Dimension must match the embedding model.

## Metadata Modeling

Example:

```sql
INSERT INTO document_chunks (document_id, chunk_index, content, metadata, embedding)
VALUES (
    101,
    0,
    'Refunds are allowed within 7 days.',
    '{"tenant_id": "acme", "category": "policy", "language": "en"}',
    '[0.1, 0.2, 0.3]'::vector
);
```

In real systems, `metadata` is often used together with relational columns, not as a full replacement.

## Better Production Schema

For high-value systems, avoid putting everything in JSONB.

A more structured design:

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_url TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tenant_id TEXT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    token_count INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Benefits:

- better filtering
- easier joins
- cleaner multitenancy
- better integrity constraints

## Ingestion Flow

Typical pipeline:

```text
raw document
   |
   v
clean text
   |
   v
split into chunks
   |
   v
generate embeddings
   |
   v
insert rows into PostgreSQL
```

## Example Ingestion with Python

```python
from openai import OpenAI
import psycopg

client = OpenAI()

texts = [
    "Refunds are allowed within 7 days.",
    "Orders can be canceled before shipping.",
]

with psycopg.connect("postgresql://localhost/mydb") as conn:
    with conn.cursor() as cur:
        for i, text in enumerate(texts):
            embedding = client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            ).data[0].embedding

            cur.execute(
                """
                INSERT INTO document_chunks (document_id, chunk_index, content, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (1, i, text, {"category": "policy"}, embedding),
            )
```

## Dimension Mismatch

This is a common operational issue.

If you switch embedding models and the dimensions change:

- old vectors and new vectors may not fit the same column
- search quality becomes inconsistent if mixed improperly

Best practice:

- store one embedding model per column/table/index strategy
- version embedding pipelines

## Multitenancy Design

For SaaS systems, always think about tenant isolation.

Options:

### 1. Shared table + `tenant_id`

Simple and common.

Needs:

- strong filtering in all queries
- good indexes on tenant metadata

### 2. Per-tenant partitions

Useful when tenants are large and isolated.

### 3. Separate databases

Strong isolation, more operational overhead.

## Soft Delete vs Hard Delete

If documents can be updated frequently, decide how to handle old embeddings.

Common patterns:

- hard delete old chunks
- soft delete with `is_active`
- version documents and only search latest active version

## Real-World Problems

### Problem: retrieval returns outdated content

Cause:

- document updated but embeddings not regenerated

Fix:

- embed refresh pipeline
- version content
- invalidate stale rows

### Problem: cross-tenant data leakage

Cause:

- missing `tenant_id` filter

Fix:

- mandatory tenant filtering
- policy checks at application layer

### Problem: duplicate chunks

Cause:

- ingestion reran without idempotency

Fix:

- upsert strategy
- unique keys on `(document_id, chunk_index, model_version)`

## Interview-Worthy Insight

If asked "How would you design a `pgvector` schema?" a strong answer is:

> I would usually store embeddings at chunk level rather than full-document level, keep strong relational identifiers like `document_id` and `tenant_id`, and store only selective flexible metadata in JSONB. I would also version the embedding model and ingestion pipeline because schema design in vector systems is really retrieval design plus operational consistency.

## Summary

Good vector search starts with good data modeling.

If the schema is weak, no index or embedding model will fully save retrieval quality.
