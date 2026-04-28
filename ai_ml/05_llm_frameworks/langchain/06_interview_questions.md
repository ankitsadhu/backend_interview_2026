# LangChain Interview Questions

## 1. What is LangChain?

LangChain is a framework for building LLM applications using reusable abstractions such as prompt templates, models, retrievers, parsers, tools, chains, and agents.

## 2. Why use LangChain instead of calling the model SDK directly?

Because real applications often need reusable prompts, structured outputs, retrieval, tool calling, and multi-step composition. LangChain helps organize those workflows more cleanly than scattered direct SDK calls.

## 3. When would you not use LangChain?

I would avoid it for very simple workflows where plain SDK code is clearer, or when framework abstraction adds more complexity than value.

## 4. What is LCEL?

LCEL stands for LangChain Expression Language. It is the composition model used to build pipelines from reusable runnables such as prompts, models, parsers, retrievers, and custom transforms.

## 5. What is a runnable?

A runnable is a composable execution unit in LangChain. Examples include prompt templates, models, output parsers, retrievers, and custom Python logic wrapped as runnable components.

## 6. What is a chain?

A chain is a sequence of steps where the output of one step feeds the next. A basic example is prompt -> model -> parser.

## 7. What is the difference between a chain and an agent?

- A chain has a fixed flow.
- An agent chooses actions dynamically, usually including tool selection.

Chains are more predictable. Agents are more flexible but riskier.

## 8. What is RAG and how does LangChain help with it?

RAG is Retrieval-Augmented Generation. LangChain helps by providing abstractions for document loading, chunking, embeddings, vector stores, retrievers, prompt composition, and answer generation.

## 9. Does RAG completely remove hallucinations?

No. It reduces hallucinations by grounding the model with retrieved context, but failures can still happen if retrieval is poor, context is noisy, or the prompt does not enforce grounded answering.

## 10. What are the main components of a LangChain RAG pipeline?

- loaders
- splitters
- embeddings
- vector store
- retriever
- prompt
- model
- parser

## 11. What are common failure modes in LangChain-based systems?

- poor chunking
- stale embeddings
- weak prompt design
- parser failures
- excessive abstraction
- wrong tool usage by agents
- token and latency explosion

## 12. How would you make a LangChain application production-ready?

I would add prompt and model versioning, structured outputs, observability, evaluation, retrieval quality checks, guarded tool use, canary rollouts, and latency/cost monitoring.

## 13. How would you decide between LangChain and LangGraph?

I would use LangChain for composable pipelines and common LLM building blocks. I would use LangGraph when the workflow is stateful, has branching logic, loops, retries, or needs durable execution.

## 14. What is the biggest mistake people make with agents?

Using agents for workflows that are actually deterministic. This adds unnecessary flexibility, risk, and debugging difficulty.

## 15. How would you reduce risk in tool-calling agents?

- use clear tool descriptions
- validate arguments
- separate read and write tools
- add approval for side effects
- cap retries and loop depth
- trace tool decisions

## 16. Why are structured outputs important?

Because backend systems usually need predictable data, not free-form text. Structured outputs improve validation, downstream integration, and reliability.

## 17. How would you debug a bad answer in a LangChain RAG pipeline?

I would inspect:

1. user query
2. retrieved documents
3. chunk quality
4. prompt grounding instructions
5. model output
6. parser behavior

Then I would add the failure as a regression evaluation case.

## 18. How would you explain LangChain in one strong interview sentence?

LangChain is an orchestration framework that provides reusable abstractions for building multi-step LLM applications such as RAG systems, structured generation pipelines, and tool-using assistants.

## Rapid-Fire Answers

### Is LangChain only for chatbots?

No. It is also useful for extraction, classification, summarization, search, document workflows, and internal copilots.

### Is LangChain mandatory for LLM apps?

No. Many apps can be built well with plain SDKs and custom code.

### What matters more in RAG, model or retrieval?

Both matter, but weak retrieval can break even a strong model.

### Should every LLM app use agents?

No. Use agents only when dynamic decision-making actually adds value.

### What should happen after a production failure?

Turn the failure into an evaluation case so the same issue is less likely to recur.

## Final Interview Tip

For LangChain interviews, always connect:

1. abstraction and composition
2. RAG and retrieval quality
3. tool calling and control
4. production reliability and tradeoffs

That combination makes answers sound senior rather than tutorial-level.
