# Chains, RAG, and Retrieval

## What is a Chain?

A chain is a sequence of steps where the output of one step becomes the input to the next.

In LangChain, a chain often looks like:

```text
user input -> prompt -> model -> parser
```

More advanced chains can include:

- retrieval
- reranking
- tool outputs
- validation
- post-processing

## Basic Chain Example

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Summarize the following text in 3 bullet points:\n\n{text}"
)

chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()

result = chain.invoke({"text": "LangChain helps structure multi-step LLM applications."})
print(result)
```

## What is RAG?

RAG stands for **Retrieval-Augmented Generation**.

Instead of asking the model to answer from its parametric memory, we:

1. retrieve relevant documents
2. inject them into the prompt
3. ask the model to answer using that context

## Why RAG Matters

RAG helps with:

- fresher information
- domain-specific grounding
- lower hallucination risk
- enterprise document Q&A

## Simple RAG Flow

```text
User Question
   |
   v
Embed query
   |
   v
Retrieve relevant chunks
   |
   v
Prompt model with context
   |
   v
Generate grounded answer
```

## Key Retrieval Components

### Document Loaders

Load source data from:

- PDFs
- web pages
- databases
- internal docs

### Text Splitters

Split long documents into chunks.

Important tradeoffs:

- chunks too small -> lose context
- chunks too large -> waste tokens

### Embeddings

Convert text into vectors for semantic search.

### Vector Stores

Store embeddings and support similarity search.

Examples:

- FAISS
- Chroma
- Pinecone
- Weaviate

### Retrievers

Expose a query interface on top of storage/search logic.

## Example: Build a Retriever

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

docs = [
    Document(page_content="LangChain supports prompt templates and LCEL."),
    Document(page_content="RAG combines retrieval with generation."),
    Document(page_content="Agents use tools to interact with external systems."),
]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

results = retriever.invoke("How does retrieval help reduce hallucinations?")
for doc in results:
    print(doc.page_content)
```

## Retrieval + Generation Example

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("""
Answer the question only from the context below.
If the answer is not in the context, say you do not know.

Question: {question}

Context:
{context}
""")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

question = "What is RAG?"
retrieved_docs = retriever.invoke(question)

answer = (prompt | llm | StrOutputParser()).invoke({
    "question": question,
    "context": format_docs(retrieved_docs),
})

print(answer)
```

## Retrieval Design Tradeoffs

### Chunk size

- small chunks improve precision
- larger chunks preserve more context

### Top-k

- low `k` can miss useful context
- high `k` increases cost and noise

### Metadata filters

Critical for:

- tenant isolation
- time-based filtering
- product-specific document subsets

## Common RAG Patterns

### 1. Basic semantic retrieval

Good starting point for small internal knowledge bases.

### 2. Hybrid retrieval

Combine semantic search with keyword or BM25 search.

Useful when exact terms matter, like:

- product IDs
- error codes
- compliance clauses

### 3. Reranking

Retrieve many candidates, then rerank the best.

Useful when first-stage retrieval is noisy.

### 4. Multi-query retrieval

Generate multiple reformulated queries to improve recall.

### 5. Contextual compression

Compress or filter retrieved context before final prompting.

## Real-World Problems

### Problem: chatbot gives generic answers

Cause:

- no retrieval
- weak grounding prompt

### Problem: answer is wrong even though source exists

Cause:

- chunking broke context
- wrong top-k
- bad embedding model
- retriever filters excluded the right doc

### Problem: answer is slow and expensive

Cause:

- too many documents in context
- repeated retrieval steps
- no reranking or compression

## Failure Modes in Production

### 1. Stale index

Documents change, but embeddings are not refreshed.

### 2. Cross-tenant leakage

Retriever filters are missing or incorrect.

### 3. Retrieval mismatch

Semantic search fails on exact identifiers like invoice numbers or policy IDs.

### 4. Prompt-grounding gap

Relevant docs are retrieved, but prompt does not force answer grounding.

## Interview-Worthy Insight

If asked "Does RAG solve hallucinations?" the best answer is:

> RAG reduces hallucinations by grounding answers in retrieved context, but it does not eliminate them. The system can still retrieve irrelevant documents, pass poor context, or generate unsupported claims unless the prompt, retrieval quality, and evaluation strategy are all strong.

## Summary

Chains are the structure.
RAG is the grounding pattern.
Retrieval quality often matters as much as model quality.
