# State, Nodes, and Edges

## The LangGraph Mental Model

At the center of LangGraph is one key idea:

**The workflow is a graph over shared state.**

That means:

- state stores the current workflow data
- nodes read and update state
- edges decide where execution goes next

## 1. State

State is the data carried across the workflow.

Good state design is very important because messy state leads to messy graphs.

### Example state

```python
from typing import TypedDict, List, Optional

class WorkflowState(TypedDict):
    user_query: str
    intent: Optional[str]
    documents: List[str]
    tool_result: Optional[str]
    approval_required: bool
    final_answer: Optional[str]
    retry_count: int
```

## Good State Design Principles

- keep state explicit
- use clear field names
- avoid dumping everything into one giant blob
- store only what downstream nodes need
- track counters and flags for safety

Helpful fields:

- `retry_count`
- `error_message`
- `current_step`
- `approval_required`
- `trace_id`

## 2. Nodes

Nodes are the units of work in the graph.

A node usually does one thing:

- classify
- retrieve
- call tool
- validate
- generate response

### Example node

```python
def classify_intent(state: WorkflowState) -> WorkflowState:
    query = state["user_query"].lower()

    if "refund" in query:
        state["intent"] = "refund"
        state["approval_required"] = True
    else:
        state["intent"] = "general"
        state["approval_required"] = False

    return state
```

Strong design rule:

Nodes should do one clear job and update state predictably.

## 3. Edges

Edges connect nodes.

They can be:

- linear
- conditional
- cyclical

### Linear edge

```text
classify -> retrieve -> generate
```

### Conditional edge

```text
if intent == "refund" -> approval
else -> generate
```

### Cyclical edge

```text
plan -> tool_call -> observe -> plan
```

## Conditional Routing

This is one of the main reasons to use LangGraph.

```python
def route_after_classification(state: WorkflowState) -> str:
    if state["approval_required"]:
        return "approval_node"
    return "generate_node"
```

This makes routing logic explicit and testable.

## Example Graph Shape

```text
START
  |
  v
classify
  |
  +--> retrieve_docs
  |      |
  |      v
  |   generate_answer
  |
  +--> approval
         |
         v
      finalize
```

## Node Types You See Often

### Classification node

Routes based on user intent.

### Retrieval node

Fetches documents, logs, or records.

### Tool node

Calls API, DB, or service tools.

### Validation node

Checks structure, safety, or policy.

### Human node

Pauses for approval or correction.

### Finalization node

Formats the final response or action.

## Design Tradeoffs

### Too few nodes

The graph becomes opaque and hard to debug.

### Too many nodes

The graph becomes fragmented and hard to maintain.

The sweet spot:

- each node should represent one meaningful step
- routing logic should be obvious

## Real-World Example: Refund Workflow

State:

- customer issue
- order info
- refund eligibility
- approval status
- final response

Possible graph:

```text
classify_request
   |
   v
fetch_order
   |
   v
check_refund_policy
   |
   +--> if high_amount -> human_approval
   |
   v
generate_response
```

This is much safer than a free-form agent improvising the entire process.

## Common Mistakes

### 1. Putting hidden business logic inside nodes

If a node contains too many unrelated decisions, the graph stops being readable.

### 2. Overloading state

Large untyped state creates accidental coupling between nodes.

### 3. Weak conditional routing

If route logic is fuzzy, the graph becomes unpredictable.

### 4. No error state

Production workflows need:

- retry count
- last error
- fallback path

## Interview-Worthy Insight

If asked "What makes LangGraph maintainable?" a strong answer is:

> Clear state design and explicit routing. I want each node to have a focused responsibility, each transition to be understandable, and the shared state to contain only the fields needed to drive the workflow. If the state is messy or nodes do too much, the graph becomes just as hard to debug as ad hoc orchestration code.

## Summary

State is the data model.
Nodes are the work units.
Edges are the control flow.

If those three are designed well, the graph stays understandable as the system grows.
