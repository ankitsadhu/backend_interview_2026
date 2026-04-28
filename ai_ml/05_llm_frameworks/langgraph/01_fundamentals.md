# LangGraph Fundamentals

## What is LangGraph?

LangGraph is a framework for building **stateful workflows** for LLM applications using a graph model.

Instead of thinking only in terms of:

- prompt -> model -> output

LangGraph helps you think in terms of:

- state
- nodes
- edges
- transitions
- loops
- checkpoints

## Why LangGraph Exists

LangChain is great for composable components and many fixed pipelines.

But some applications need more explicit workflow control:

- agent loops
- conditional branching
- retries
- approval steps
- resumable execution
- long-running workflows

If you build those using only ad hoc chain composition, the code can become hard to reason about.

LangGraph exists to make workflow control explicit.

## When You Need LangGraph

Use LangGraph when your system needs:

- state across multiple steps
- dynamic routing based on intermediate results
- cycles like tool-call -> observe -> plan -> tool-call
- pause / resume behavior
- controllable agents

## LangGraph vs LangChain

This is one of the most important interview questions.

### LangChain

Best for:

- prompts
- models
- parsers
- retrievers
- simple chains
- common LLM abstractions

### LangGraph

Best for:

- stateful workflows
- branching logic
- loops
- retries
- approval checkpoints
- durable agent execution

Simple rule:

- LangChain gives reusable building blocks
- LangGraph gives explicit control flow over those blocks

## Core Concepts

### 1. State

State is the shared data that moves through the workflow.

Examples:

- user query
- retrieved docs
- tool results
- intermediate reasoning
- approval status
- retry count
- final answer

### 2. Node

A node is a processing step.

Examples:

- classify intent
- retrieve context
- call tool
- validate output
- ask human for approval

### 3. Edge

An edge defines what step comes next.

This can be:

- fixed
- conditional
- cyclical

### 4. Graph

A graph is the full workflow of nodes and transitions.

## Why the Graph Model Matters

Because many real agent systems are not linear.

Example:

```text
User request
   |
   v
Plan step
   |
   +--> Need tool? yes -> call tool
   |                     |
   |                     v
   |                update state
   |                     |
   +<--------------------+
   |
   v
Generate final answer
```

That loop is awkward in a simple chain, but natural in a graph.

## Example State Definition

```python
from typing import TypedDict, List

class AgentState(TypedDict):
    user_query: str
    retrieved_docs: List[str]
    tool_result: str
    retry_count: int
    final_answer: str
```

This typed state makes workflow data explicit and easier to debug.

## Minimal Conceptual Example

```python
def classify_node(state):
    query = state["user_query"]
    state["route"] = "retrieve" if "policy" in query.lower() else "answer_directly"
    return state

def direct_answer_node(state):
    state["final_answer"] = "This can be answered directly."
    return state
```

Even in a simple example, the benefit is clarity:

- state is explicit
- route decision is explicit
- next step is explicit

## Real-World Use Cases

### 1. Support agent with approval

Flow:

- classify request
- fetch order
- check refund eligibility
- ask human before refund
- finalize response

### 2. Enterprise research assistant

Flow:

- understand query
- retrieve docs
- rerank docs
- verify citations
- generate answer

### 3. Incident investigation agent

Flow:

- classify incident
- query metrics
- query logs
- summarize
- request human confirmation before action

## Common Misconceptions

### "LangGraph is only for autonomous agents"

No. It is for any workflow that benefits from explicit state and transitions.

### "LangGraph replaces LangChain"

No. They are complementary. LangChain components are often used inside LangGraph nodes.

### "If I use a graph, the system becomes reliable automatically"

No. You still need observability, evaluation, safety checks, and careful node design.

## MANG-Level Interview Insight

If asked "Why use LangGraph?" a strong answer is:

> I use LangGraph when the LLM workflow becomes stateful and non-linear. Chains are good for straightforward pipelines, but once I need branching, loops, retries, human checkpoints, or resumability, I want the workflow represented explicitly as a graph so it is easier to reason about, test, and operate.

## Summary

LangGraph becomes valuable when your LLM application is no longer just a pipeline.

It is the right abstraction when the workflow itself becomes part of the engineering problem.
