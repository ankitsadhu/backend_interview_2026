# Workflows and Agent Loops

## Why Workflows Need More Than Chains

Chains are great when the path is fixed.

But many real systems need:

- branch if condition A, else B
- retry when validation fails
- loop until tool results are sufficient
- escalate to human when risk is high

This is where LangGraph shines.

## Typical Workflow Patterns

### 1. Fixed pipeline with explicit state

Even a simple flow can benefit from clear state:

```text
ingest -> retrieve -> generate -> validate
```

### 2. Conditional routing

```text
classify -> if billing then billing_flow else support_flow
```

### 3. Retry loop

```text
generate -> validate -> if invalid then regenerate
```

### 4. Agent loop

```text
plan -> choose_tool -> execute_tool -> observe -> plan
```

## Example: Conditional Workflow

```python
from typing import TypedDict, Optional

class State(TypedDict):
    query: str
    route: Optional[str]
    result: Optional[str]

def classify(state: State) -> State:
    state["route"] = "billing" if "invoice" in state["query"].lower() else "general"
    return state

def billing_node(state: State) -> State:
    state["result"] = "Handled by billing workflow"
    return state

def general_node(state: State) -> State:
    state["result"] = "Handled by general workflow"
    return state
```

This is trivial, but it illustrates the pattern:

- classify once
- route explicitly
- keep nodes focused

## Agent Loop Pattern

Agent loops are one of the biggest LangGraph use cases.

### Why not just use a normal agent abstraction?

Because in production you often need:

- loop limits
- explicit state
- tool-use visibility
- approval before side effects
- custom routing on failure

### Conceptual loop

```text
START
  |
  v
plan
  |
  v
need_tool?
  |
  +--> no -> finalize
  |
  +--> yes -> call_tool
               |
               v
            update_state
               |
               v
              plan
```

This gives you explicit control over what would otherwise be hidden inside a general-purpose agent loop.

## Example: Tool Retry Pattern

```python
class RetryState(TypedDict):
    tool_result: Optional[str]
    retry_count: int
    done: bool

def validate_tool_result(state: RetryState) -> str:
    if state["tool_result"]:
        return "finalize"
    if state["retry_count"] >= 2:
        return "fallback"
    return "retry_tool"
```

This is useful because retries become part of the graph design, not accidental side effects.

## Workflow Pattern: Retrieval + Validation

In enterprise RAG systems, a strong workflow is often:

```text
understand_query
   |
   v
retrieve_docs
   |
   v
check_retrieval_quality
   |
   +--> poor quality -> reformulate_query
   |
   v
generate_answer
   |
   v
validate_citations
   |
   +--> invalid -> regenerate
   |
   v
finalize
```

This is a much more robust flow than:

- retrieve once
- generate once
- hope for the best

## Workflow Pattern: Support Copilot

Possible graph:

```text
classify_ticket
   |
   +--> refund_flow
   |      |
   |      +--> fetch_order
   |      +--> check_policy
   |      +--> human_approval_if_needed
   |      +--> finalize
   |
   +--> faq_flow
          |
          +--> retrieve_knowledge
          +--> generate_answer
          +--> finalize
```

The benefit is that each path is explicit and auditable.

## Common Failure Modes in Agent Loops

### 1. Infinite loops

Cause:

- no stop condition
- bad planner logic
- repeated unsuccessful tool usage

Fix:

- add max iterations
- track retry count in state
- add fallback / exit node

### 2. Tool thrashing

Cause:

- agent keeps switching between tools without progress

Fix:

- better route logic
- explicit planner node
- constraints on tool sequence

### 3. Hidden failure propagation

Cause:

- tool error is swallowed and later nodes operate on bad state

Fix:

- explicit error fields in state
- error routing path
- validation node after important tool calls

## MANG-Level Interview Insight

If asked "Why is LangGraph useful for agent workflows?" a strong answer is:

> Because it turns an implicit agent loop into an explicit, stateful workflow. That makes it easier to bound the loop, insert validation and human approvals, route on failures, and reason about retries or side effects. In production, explicit control flow is usually more reliable than hidden orchestration logic.

## Summary

LangGraph is powerful because it lets you model:

- non-linear workflows
- retries
- loops
- recoverable failure paths
- controlled agent behavior
