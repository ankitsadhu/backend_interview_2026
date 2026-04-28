# Mock System Design: RAG Systems

This file contains **MANG-style mock system design scenarios** for RAG systems.

The goal is not just to memorize one architecture, but to learn how to:

- clarify requirements
- choose the right baseline
- identify tradeoffs
- separate retrieval failures from generation failures
- talk like a strong production-minded engineer

## How to Answer in an Interview

A strong structure:

1. clarify requirements
2. define success metrics
3. propose baseline architecture
4. discuss data model and retrieval strategy
5. discuss scaling and failure modes
6. discuss evaluation and rollout

Good candidates do not jump straight into "use vector DB."

---

## Scenario 1: Enterprise Policy Assistant

### Prompt

Design an internal assistant that answers employee questions from company policy documents.

Examples:

- "What is the maternity leave policy?"
- "Can I carry forward unused vacation days?"
- "What is the travel reimbursement limit?"

### Clarify Requirements

Ask:

- How fresh must answers be?
- Do answers need citations?
- Is the data multi-tenant or single-company?
- Which document sources matter: PDFs, wiki, HR portal?
- What is the latency target?
- What languages are supported?

### Core Requirements

- grounded answers from internal policy docs
- citations
- fast enough for interactive use
- ability to abstain
- easy updates when policy changes

### Strong Baseline Design

```text
Policy docs
  -> parse
  -> chunk by section
  -> embed
  -> store in pgvector with metadata

User query
  -> embed
  -> retrieve filtered chunks
  -> optionally fetch neighbor chunks
  -> prompt LLM with grounding instructions
  -> answer with citations
```

### Key Data Design

Metadata:

- policy type
- policy version
- language
- effective date
- source URL

Why it matters:

- filters improve retrieval
- versions support freshness
- citations improve trust

### Retrieval Strategy

- semantic search for natural language questions
- maybe hybrid search for exact policy names
- top-k of 3 to 5 to start
- fetch neighboring chunks if clauses span boundaries

### Main Failure Modes

- stale policies
- wrong citations
- chunk boundaries cut clauses badly
- answer synthesis ignores context

### Strong Interview Answer

> I would start with a simple filtered RAG pipeline using policy-section chunking, `pgvector` storage, and a prompt that forces grounded answers with citations or abstention. I would version documents and monitor freshness because policy assistants fail badly if the right document is retrieved but outdated.

---

## Scenario 2: Customer Support Copilot

### Prompt

Design a support assistant that helps agents answer customer questions using help docs, policy docs, and customer account context.

Examples:

- "Can this user get a refund?"
- "Why was this order delayed?"
- "How should I respond to this complaint?"

### Clarify Requirements

Ask:

- Is this internal agent assist or customer-facing?
- Does it need real-time account/order data?
- Can it trigger actions or only provide recommendations?
- Are there regulatory or refund approval constraints?

### Core Observation

This is usually not pure RAG.

It is often:

- retrieval
- plus tools
- plus workflow logic

### Good Architecture

```text
User / support agent query
   |
   v
classify query
   |
   +--> knowledge retrieval path
   +--> account tool path
   +--> combined path
   |
   v
gather evidence
   |
   v
generate grounded recommendation
   |
   v
optional human approval for risky actions
```

### Why LangGraph May Help

Because the flow may need:

- query classification
- policy retrieval
- order lookup
- validation
- approval before refund suggestions

### Retrieval Considerations

- docs and policies in `pgvector`
- account/order data from tools, not embeddings
- hybrid route if order ID appears

### Main Risks

- wrong customer context
- wrong refund advice
- unsupported answer combining retrieved docs and stale account state
- too much hidden orchestration complexity

### Strong Interview Answer

> I would not treat this as a pure semantic search problem. Support copilots often need both retrieved knowledge and live operational data, so I would separate document retrieval from account tools, route queries explicitly, and require approval for recommendations that could trigger business or financial actions.

---

## Scenario 3: Codebase Assistant

### Prompt

Design a RAG system that answers questions about a company codebase.

Examples:

- "Where is payment retry logic implemented?"
- "How does auth token refresh work?"
- "Which service calls Stripe?"

### Clarify Requirements

Ask:

- Should it answer or also modify code?
- How fresh must it be with recent commits?
- Is repo size moderate or very large?
- Should it support cross-repo search?

### Data Challenges

Code is different from prose.

Need to preserve:

- file path
- symbol names
- function/class boundaries
- comments and docstrings
- commit freshness

### Ingestion Design

- parse repo files
- chunk by function/class or logical block
- store path, symbol, language, repo metadata
- embed chunks

### Retrieval Strategy

- semantic search for conceptual questions
- lexical search for exact symbols, filenames, error strings
- hybrid search is especially important here

### Why Hybrid Search Matters

Because exact strings matter a lot in code:

- `AuthService`
- `refresh_token`
- `charge_customer`

Pure semantic search is not enough.

### Main Failure Modes

- stale code index after deploys
- chunking across function boundaries
- poor cross-file reasoning
- assistant answers from general coding patterns rather than retrieved code

### Strong Interview Answer

> For codebase RAG I would use structure-aware chunking around symbols, preserve path and symbol metadata, and combine semantic and lexical retrieval because exact identifiers matter heavily in code search. I would also prioritize index freshness because code assistants degrade quickly if retrieval lags behind the actual repository state.

---

## Scenario 4: Research Analyst Assistant

### Prompt

Design an assistant that helps analysts answer questions from long reports, PDFs, earnings calls, and internal notes.

Examples:

- "What are the major revenue risks this quarter?"
- "Compare management commentary across the last 3 earnings calls."
- "What evidence supports the claim that margins will improve?"

### Why This is Hard

This requires more than naive retrieval.

Problems:

- multi-document synthesis
- long context
- ambiguous evidence
- need for citations

### Strong Design

```text
query understanding
   |
   v
retrieve candidates from multiple sources
   |
   v
rerank
   |
   v
group evidence by source / theme
   |
   v
generate answer with citations
```

### Useful Enhancements

- query rewrite
- source diversity in retrieval
- citation validation
- iterative retrieval if evidence weak

### Main Risks

- model over-compresses nuance
- one source dominates answer
- citations are present but weak
- long reports are chunked poorly

### Strong Interview Answer

> For analyst workflows I would optimize for evidence quality and citation structure, not just one-shot answer fluency. I would likely retrieve from multiple sources, rerank for relevance, encourage source diversity, and force the model to ground each major claim in retrieved evidence rather than letting it produce a generic synthesis.

---

## Scenario 5: Multi-Tenant Enterprise RAG Platform

### Prompt

Design a shared RAG platform used by many enterprise customers, each with separate documents and permissions.

### First Principle

This is a retrieval quality problem and a data isolation problem.

### Core Requirements

- strict tenant isolation
- document freshness
- per-tenant indexing
- observability
- cost control

### Architecture Considerations

- shared tables with `tenant_id` filters vs tenant-level partitions
- per-tenant metadata and access control
- ingestion queues
- retriever versioning
- offline eval sets per tenant or customer segment

### Biggest Risks

- cross-tenant leakage
- stale embeddings for one tenant
- noisy small tenants drowning in shared retrieval strategy
- operational cost explosion

### Strong Interview Answer

> In a multi-tenant RAG platform, access control is more important than clever retrieval. I would design mandatory tenant-aware filtering into the retrieval layer, version ingestion per tenant, and monitor freshness and quality by tenant slice because regressions are often customer-specific rather than global.

---

## Cross-Scenario Follow-Up Questions

Interviewers often ask follow-ups like these.

### 1. How do you know whether the issue is retrieval or generation?

Strong answer:

Inspect whether the correct evidence was retrieved. If not, it is retrieval failure. If yes but the answer is still unsupported or wrong, it is generation failure.

### 2. When do you add reranking?

Strong answer:

After establishing a baseline, if top-k retrieval has acceptable recall but poor precision.

### 3. When would you use fine-tuning along with RAG?

Strong answer:

Use fine-tuning for output behavior or domain style, and RAG for current knowledge.

### 4. When do you move beyond LangChain baseline to LangGraph?

Strong answer:

When the workflow becomes stateful or non-linear, such as iterative retrieval, multi-tool evidence gathering, or human approval steps.

### 5. How do you make the system trustworthy?

Strong answer:

Require citations, allow abstention, trace retrieved chunks, evaluate groundedness, and monitor unsupported-answer rates.

---

## What Great Answers Sound Like

Weak answer:

- "Use embeddings and a vector DB."

Strong answer:

- clarifies data freshness and security
- discusses chunking and metadata
- separates retrieval from generation
- proposes a simple baseline before advanced orchestration
- explains failure modes and evaluation

---

## Final Interview Tip

For RAG system design interviews:

- start simple
- design for grounding
- treat ingestion as first-class
- separate retrieval from generation
- discuss trust, latency, cost, and safety

That combination is what makes the answer sound MANG-level rather than tutorial-level.
