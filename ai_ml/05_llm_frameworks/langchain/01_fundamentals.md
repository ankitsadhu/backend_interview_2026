# LangChain Fundamentals

## What is LangChain?

LangChain is a framework for building applications around LLMs using modular components.

Instead of writing everything manually, it provides reusable abstractions for:

- prompts
- model invocation
- parsers
- retrievers
- memory-like state patterns
- tools
- chains
- agents

## Why LangChain Exists

A raw LLM API call is simple:

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Explain vector databases"}],
)

print(response.choices[0].message.content)
```

That is fine for very small demos.

But real applications usually need:

- reusable prompts
- structured outputs
- retrieval from documents
- multi-step workflows
- tools and APIs
- consistent composition
- observability

LangChain helps organize those concerns.

## What Problem Does It Solve?

Without a framework, teams often end up with:

- prompt strings scattered across files
- ad hoc parsing logic
- duplicate model wrappers
- tightly coupled retrieval code
- spaghetti agent logic

LangChain aims to make LLM workflows:

- composable
- testable
- reusable
- easier to reason about

## Core Abstractions

### 1. Prompt Templates

Prompt templates separate prompt structure from runtime data.

### 2. Models

LangChain wraps chat models and text models behind common interfaces.

### 3. Output Parsers

Parsers convert raw model output into structured data.

### 4. Retrievers

Retrievers fetch relevant context for RAG.

### 5. Chains / Runnables

Chains compose multiple steps into one pipeline.

### 6. Tools and Agents

Tools let the model interact with external systems. Agents decide which tools to use and in what order.

## Simple LangChain Example

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a concise interview coach."),
    ("human", "Explain {topic} in simple terms."),
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chain = prompt | llm

response = chain.invoke({"topic": "LangChain"})
print(response.content)
```

This is better than raw API code because prompt and model are cleanly separated and composable.

## Where LangChain Fits

```text
Application Layer
  FastAPI / backend service / worker / agent service

Orchestration Layer
  LangChain

Model + Data Layer
  LLM providers / vector DB / APIs / databases / tools

Observability Layer
  LangSmith and normal monitoring tools
```

## LangChain vs Plain SDK Calls

### Plain SDK is often enough when:

- one or two LLM calls
- no retrieval
- no tools
- little reuse needed

### LangChain is helpful when:

- prompts are reused across workflows
- you need multi-step composition
- you need RAG
- you need tool calling
- you want standardized building blocks

## LangChain vs LangGraph

This is a common interview question.

### LangChain

Best for:

- prompt pipelines
- simple chains
- RAG flows
- basic tool integration

### LangGraph

Best for:

- explicit stateful workflows
- branching logic
- cycles and retries
- durable agent execution

Simple rule:

- use LangChain for composable building blocks
- use LangGraph when the workflow itself becomes a graph with state transitions

## Real-World Problems LangChain Helps Solve

### 1. Build a support bot with retrieval

Need:

- prompt template
- retriever
- model
- output formatting

### 2. Build an assistant that queries internal tools

Need:

- tool schema
- chat model with tool calling
- orchestration and validation

### 3. Build a document summarization pipeline

Need:

- loaders
- chunking
- summarization prompt
- map-reduce or refine style chain

## Common Misconceptions

### "LangChain is only for chatbots"

No. It is useful for:

- extraction
- classification
- summarization
- Q&A
- search assistants
- workflow automation

### "LangChain removes the need to understand LLMs"

No. You still need to understand:

- prompting
- token limits
- hallucinations
- evaluation
- retrieval quality

### "Using a framework automatically means production-ready"

No. Frameworks help structure code, but production quality depends on:

- evaluation
- observability
- safe rollouts
- privacy
- latency and cost control

## When Not to Use LangChain

A strong candidate should say this clearly.

Avoid LangChain if:

- the use case is trivial
- abstraction overhead hurts clarity
- the team needs maximum low-level control
- debugging framework behavior becomes harder than custom code

## MANG-Level Interview Insight

Interviewers do not just want to hear "LangChain helps build LLM apps."

A better answer is:

> LangChain provides composable abstractions for common LLM application patterns like prompt templating, retrieval, output parsing, and tool calling. It helps organize multi-step workflows so that applications are easier to evolve than a pile of direct SDK calls. But I would still evaluate whether the abstraction is worth it for the complexity of the use case, because for simple flows raw SDK code may be clearer.

## Summary

LangChain is useful when LLM logic becomes a system rather than a single API call.

It is most valuable when you need composition, reuse, and cleaner workflow structure.
