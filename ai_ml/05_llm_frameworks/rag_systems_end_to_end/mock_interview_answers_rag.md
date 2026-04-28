# Mock Interview Answers: RAG Systems

This file contains **spoken-answer style responses** for RAG interviews.

The goal is to help you answer naturally in a MANG interview, not just remember bullet points.

Each answer is written in a way you could actually say out loud in roughly **2 to 4 minutes**, followed by shorter follow-up answers where useful.

## How to Use This File

Practice each answer in three forms:

1. full answer
2. compressed 60-second version
3. follow-up defense version

That is how strong candidates sound fluent instead of memorized.

---

## 1. Design an Enterprise Policy Assistant

### Full Answer

If I were designing an enterprise policy assistant, I would first clarify a few things: how fresh the policies need to be, whether answers must include citations, whether the assistant is internal-only, and whether there are language or compliance constraints. Those details matter because they affect ingestion, retrieval, and trust requirements.

My baseline design would be a filtered RAG system rather than jumping straight into agents. On the ingestion side, I would parse the source documents, chunk them in a structure-aware way, ideally by section or clause rather than fixed-size chunks, generate embeddings, and store them in Postgres with `pgvector`. I would keep metadata like policy type, policy version, language, effective date, and source URL. That metadata is important because semantic similarity alone is not enough in enterprise settings.

At query time, I would embed the user query, retrieve the top few chunks with mandatory filters, maybe fetch neighboring chunks if policy clauses span chunk boundaries, and then prompt the model with strict grounding instructions. I would explicitly tell the model to answer only from retrieved context and say it does not know if the context is insufficient. I would also require citations in the final answer because trust matters a lot for policy systems.

For quality, I would evaluate retrieval and generation separately. Retrieval metrics would tell me whether I found the right evidence, while answer evaluation would tell me whether the model actually used that evidence correctly. In production, I would trace query, retrieved chunks, prompt version, and final answer so I can debug whether failures come from stale docs, weak chunking, or generation behavior.

I would start with this simple baseline first because many policy assistants do not need fancy agent workflows. If later I saw cases where users asked more complex multi-document or workflow-driven questions, then I would consider adding reranking or graph-based orchestration.

### 60-Second Version

I would design it as a filtered RAG system. I would chunk policy documents by logical sections, store embeddings plus strong metadata in `pgvector`, retrieve a small set of relevant chunks with required filters, and prompt the model to answer only from that context with citations or abstain if evidence is weak. I would version policies and monitor freshness because stale documents are a major risk. I would also evaluate retrieval separately from generation so I know whether failures come from bad search or bad answer synthesis.

### Good Follow-Up: Why Not Fine-Tune?

Because the main problem here is dynamic policy knowledge, not behavior adaptation. Fine-tuning is weak for frequently changing policy content. RAG is the right first choice because it keeps the assistant grounded in the latest documents.

---

## 2. Design a Customer Support Copilot

### Full Answer

For a customer support copilot, I would first clarify whether it is customer-facing or internal agent assist, whether it can take actions or only make recommendations, and whether it needs access to live customer state such as order status, refunds, or CRM records. That matters because this is usually not a pure RAG system. It is often retrieval plus tools plus workflow logic.

I would separate the system into two evidence paths. One path would retrieve static or semi-static knowledge such as help docs, refund policies, and troubleshooting guides. That content would be ingested, chunked, embedded, and stored in something like `pgvector` with metadata like product, region, language, and policy version. The second path would use live tools for operational data such as order lookup, account state, or refund eligibility. I would not try to encode live account state into a vector store.

At query time, I would first classify the request. Some questions are pure FAQ and only need document retrieval. Some are account-specific and need tools. Some require both. I would then gather evidence from the right path, combine it into a grounded prompt, and have the model generate a recommendation or draft response. If the workflow involves risky business actions, like refund recommendations or compliance-sensitive suggestions, I would insert approval gates and keep those actions out of an unconstrained agent loop.

For orchestration, I would start simple with a chain if the workflow is mostly deterministic. If the request routing, retrieval, tool usage, and validation become more complex, I would move to a LangGraph-style explicit workflow so the control flow stays understandable.

For evaluation, I would measure more than answer quality. I would track policy retrieval correctness, recommendation accuracy, escalation rate, agent acceptance rate, and unsupported-answer incidents. I would also trace which documents and tools were used so on-call engineers can debug bad recommendations quickly.

### 60-Second Version

I would treat support copilot as retrieval plus live tools, not pure RAG. Static knowledge like policies would live in `pgvector`, while live customer or order state would come from tools. I would classify requests into doc-only, tool-only, or combined flows, gather the right evidence, and generate grounded recommendations. For risky actions, I would require validation or approval. The biggest mistake would be trying to answer account-specific questions from semantic retrieval alone.

### Good Follow-Up: Why Might LangGraph Help?

Because support copilots often need explicit routing, validation, and approval steps. Once the workflow becomes non-linear, a graph model is easier to reason about than hidden agent logic.

---

## 3. Design a Codebase Assistant

### Full Answer

For a codebase assistant, I would begin by clarifying whether the assistant is only answering questions or also making edits, whether it must reflect the latest commits, and whether it spans one repository or many. Code retrieval is different from document retrieval because exact identifiers matter a lot.

On the ingestion side, I would avoid naive fixed-size chunking. Instead, I would chunk by meaningful code structure, such as functions, classes, modules, or logical blocks, while preserving metadata like file path, symbol name, repository, language, and maybe commit SHA or index version. That structure matters because developers often ask questions tied to symbols or files, not just generic semantics.

For retrieval, I would use hybrid search. Semantic search is useful for conceptual questions like "where is retry logic implemented," but lexical search is critical for exact strings like `AuthService`, `refresh_token`, or error codes. So I would combine lexical and vector retrieval rather than relying on only one.

At answer time, I would provide the retrieved code snippets, paths, and maybe a small amount of surrounding context, then prompt the model to answer based only on that evidence. If the assistant is expected to explain cross-file behavior, I might also retrieve neighboring call sites or dependency metadata rather than only isolated chunks.

The biggest production risk is freshness. Code assistants degrade quickly if the index lags behind the repository. I would therefore make index refresh part of the CI or ingestion pipeline, and I would version the retrieval corpus so failures can be tied back to a specific repo snapshot.

### 60-Second Version

For a codebase assistant, I would use structure-aware chunking around functions and classes, preserve metadata like file path and symbol, and combine semantic plus lexical retrieval because exact identifiers matter heavily in code. I would optimize for freshness by keeping the index tied closely to repo updates, and I would ground answers in retrieved code rather than letting the model answer from generic coding intuition.

### Good Follow-Up: Why Not Pure Vector Search?

Because code search depends heavily on exact identifiers, filenames, and error strings. Semantic similarity helps, but hybrid retrieval is usually the stronger design.

---

## 4. Design a Research Analyst Assistant

### Full Answer

For a research analyst assistant, I would clarify whether the main goal is summarization, evidence gathering, cross-document comparison, or recommendation support. I would also ask whether citations are mandatory and whether analysts care more about recall or precision. In research workflows, evidence quality matters a lot more than answer fluency alone.

My ingestion pipeline would preserve source structure carefully. Long reports, earnings calls, and internal notes would be chunked in a way that keeps section boundaries, speaker context, and timestamps where relevant. I would store source metadata such as report name, date, section, and document type, because analysts often care about where a claim came from.

For retrieval, I would not rely on one-shot nearest-neighbor search alone. I would likely retrieve from multiple sources, rerank for precision, and encourage source diversity so the answer is not dominated by one document. If the question is broad, like comparing management commentary across quarters, I might use an iterative or staged retrieval pattern where the system retrieves, sees evidence gaps, and fetches more.

At answer time, I would require evidence-backed synthesis. I would want each major claim to be tied to one or more retrieved sources, and I would likely prefer a structured answer with claim-plus-citation style rather than a free-form paragraph.

For evaluation, I would focus on groundedness, citation quality, evidence completeness, and whether the assistant misses important counter-evidence. A common failure in research assistants is sounding polished but missing nuance, which is why I would test source diversity and completeness, not only relevance.

### 60-Second Version

For a research assistant, I would optimize for evidence-backed synthesis rather than one-shot fluent summaries. I would preserve document structure during ingestion, retrieve from multiple sources, rerank for precision, and require citations for major claims. If questions are broad, I would use staged retrieval instead of naive one-shot search. The biggest risk here is producing confident summaries that omit or distort the evidence.

### Good Follow-Up: Why Might Baseline RAG Be Insufficient?

Because research questions often require multi-document synthesis, source diversity, and iterative retrieval. A naive top-k prompt may miss important evidence or overweight one source.

---

## 5. Design a Multi-Tenant Enterprise RAG Platform

### Full Answer

For a multi-tenant RAG platform, my first concern would be isolation and correctness before clever retrieval. I would clarify tenant size distribution, document freshness requirements, permission granularity, and whether the platform must support per-tenant customization in retrieval or prompting.

Architecturally, I would design the system so every chunk carries strong metadata like `tenant_id`, document version, source type, and access labels. Depending on scale, I would choose between a shared table with mandatory tenant filters or stronger physical isolation like partitioning. The most important point is that access control must not be left as an afterthought. A retrieval system that occasionally leaks another tenant’s documents is unacceptable.

The ingestion layer should be tenant-aware and versioned. Different tenants may upload documents at different rates and quality levels, so I would track freshness and index lag per tenant rather than only globally. At query time, I would first enforce tenant and permission filters, then run retrieval, optionally rerank, and generate grounded answers with citations.

From an ops perspective, I would monitor quality by tenant slice because regressions are often customer-specific. I would also version chunking strategy, retriever logic, prompt version, and index version so that I can debug regressions cleanly. If one tenant has very large data volume or special performance needs, I might isolate their storage or retrieval path rather than over-optimizing the entire shared system.

### 60-Second Version

In a multi-tenant RAG platform, I would prioritize tenant isolation, freshness, and observability over fancy retrieval tricks. Every chunk would carry strong metadata, tenant-aware filtering would be mandatory, ingestion would be versioned per tenant, and quality would be monitored by tenant slice. The biggest risk is cross-tenant leakage, so I would design access control directly into the retrieval layer rather than bolting it on later.

### Good Follow-Up: When Would You Partition by Tenant?

I would consider it when tenants are large enough that isolation, query performance, or operational independence justify the added complexity.

---

## 6. How Would You Evaluate a RAG System End to End?

### Full Answer

I would evaluate retrieval and generation separately because combining them into one single score hides the root cause of failures. On the retrieval side, I would look at recall@k, precision@k, whether the correct evidence was retrieved, and whether citations point to the right chunks. On the generation side, I would look at correctness, groundedness, completeness, abstention quality, and format compliance if the answer needs to be structured.

I would build an offline dataset from real queries, hard production failures, ambiguous questions, exact-ID queries, long-context cases, and no-answer cases. Then I would run controlled experiments when changing chunking, embeddings, retriever logic, prompt version, or reranking. I would not rely only on overall averages; I would slice results by tenant, query type, domain, and workflow.

In production, I would trace the full pipeline: user query, rewritten query if any, retrieved chunk IDs, prompt version, model version, and final answer. This makes it possible to debug whether a failure came from bad retrieval, stale documents, or weak grounding instructions. I would also track latency, cost, user feedback, and escalation rate because a RAG system can be technically accurate but still fail as a product.

### 60-Second Version

I would split evaluation into retrieval and generation. Retrieval tells me whether the right evidence was found, and generation tells me whether the model used that evidence correctly. I would build offline datasets from real queries and failure cases, trace the full pipeline in production, and monitor groundedness, latency, cost, and user feedback together. The key principle is that RAG failures are usually pipeline failures, not just model failures.

---

## 7. When Would You Use RAG vs Fine-Tuning?

### Full Answer

I think of RAG and fine-tuning as solving different problems. RAG is primarily for knowledge grounding. It is the right choice when the answer depends on fresh, private, or frequently changing information. Fine-tuning is more about changing behavior: improving style, structure, instruction following, or domain-specific output patterns.

So if I am building something like a policy assistant, support knowledge bot, or codebase assistant, my first instinct is RAG because the problem is access to external knowledge. If I am building something that needs more consistent structured summaries, domain-specific tone, or task-specific outputs, then fine-tuning becomes more attractive.

In practice, strong systems often use both. For example, I might fine-tune a model to produce concise structured outputs, but still use RAG to provide current evidence. I would avoid trying to fine-tune dynamic knowledge into weights because that creates freshness and maintenance problems.

### 60-Second Version

RAG is for knowledge, fine-tuning is for behavior. If the main issue is fresh or private information, I would use RAG. If the main issue is output consistency, style, or task adaptation, I would consider fine-tuning. In practice, I often combine them: RAG for evidence and fine-tuning for how the model behaves.

---

## Quick Delivery Tips

When speaking these answers:

- open with clarifying requirements
- keep the baseline simple first
- say "I would start with..."
- separate retrieval from generation explicitly
- mention one or two failure modes proactively
- end with evaluation and rollout

That structure makes you sound calm, senior, and systematic.
