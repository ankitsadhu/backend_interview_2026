# Building RAG with pgvector and LangChain

## Why This Stack is Practical

For many teams, a very practical baseline stack is:

- PostgreSQL
- `pgvector`
- LangChain
- one hosted LLM

Why:

- operational simplicity
- SQL + metadata filtering
- reusable chain abstractions
- fast path to a working RAG system

## Reference Architecture

```text
Ingestion Job
  -> parse docs
  -> chunk docs
  -> embed docs
  -> store in PostgreSQL + pgvector

Query Service
  -> embed user query
  -> retrieve top-k chunks from pgvector
  -> build prompt with context
  -> call LLM
  -> return grounded answer
```

## Example Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    document_id BIGINT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    source_type TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Example Similarity Query

```sql
SELECT
    id,
    document_id,
    content
FROM document_chunks
WHERE tenant_id = $1
ORDER BY embedding <=> $2::vector
LIMIT 5;
```

This is the simplest useful retrieval baseline.

## Python Retrieval Example with psycopg

```python
import psycopg

def retrieve_chunks(conn, tenant_id: str, query_embedding: list[float], k: int = 5):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, content
            FROM document_chunks
            WHERE tenant_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (tenant_id, query_embedding, k),
        )
        return cur.fetchall()
```

## Prompt Construction

A grounded prompt should usually:

- tell the model to answer only from context
- tell the model to say it does not know if context is insufficient
- optionally require citations

## LangChain Example

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("""
You are a grounded enterprise assistant.
Answer only from the provided context.
If the answer is not in the context, say you do not know.

Question: {question}

Context:
{context}
""")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm | StrOutputParser()

def format_context(rows):
    return "\n\n".join(row[1] for row in rows)
```

Then:

```python
result = chain.invoke({
    "question": "What is the refund policy?",
    "context": format_context(retrieved_rows),
})
```

## End-to-End Flow Example

```python
from openai import OpenAI
import psycopg

client = OpenAI()

def embed_query(query: str) -> list[float]:
    return client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    ).data[0].embedding

def answer_question(conn, tenant_id: str, question: str) -> str:
    query_embedding = embed_query(question)
    rows = retrieve_chunks(conn, tenant_id, query_embedding, k=5)
    context = format_context(rows)
    return chain.invoke({"question": question, "context": context})
```

## Improving the Baseline

Once baseline works, common upgrades are:

- fetch neighboring chunks
- hybrid retrieval
- reranking
- citations
- structured output
- caching

## Why LangChain Helps Here

LangChain helps keep the generation side clean:

- prompt templates
- output parsing
- chain composition
- easier swap of model provider

It does not remove the need for good retrieval design.

## Common Mistakes

### 1. Building a fancy chain on weak retrieval

No framework can save poor chunk quality.

### 2. No abstain behavior

The model fills gaps with hallucinations.

### 3. Passing too many chunks

Large context windows can reduce precision and increase cost.

### 4. No tenant filter

Unsafe and incorrect retrieval.

## Real-World Example: Internal Policy Assistant

Good baseline:

- chunk policy docs by section
- store metadata like `tenant_id`, `policy_type`, `version`
- retrieve with cosine distance
- build prompt with top 3 to 5 chunks
- require "I do not know" when context is missing

This is a realistic strong baseline for interviews.

## MANG-Level Interview Insight

If asked "How would you build a simple production-minded RAG system?" a strong answer is:

> I would start with a clean ingestion pipeline, chunk documents carefully, store embeddings and metadata in `pgvector`, retrieve with mandatory filters, and build a grounded LangChain prompt that forces the model to answer only from retrieved context or abstain. Then I would evaluate the baseline before adding more complex features like reranking or graph-based orchestration.

## Summary

The best baseline RAG systems are:

- simple
- grounded
- filtered
- measurable
