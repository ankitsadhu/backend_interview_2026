# Agents and Tool Calling

## What is a Tool?

A tool is a function or external capability the model can use.

Examples:

- search internal docs
- query SQL
- fetch order status
- call a REST API
- send an email

In production, tools often expose the model to real systems, so design matters a lot.

## What is an Agent?

An agent is a system where the model chooses:

- whether to use a tool
- which tool to use
- with what arguments
- when to stop

This is more flexible than a fixed chain, but also riskier.

## Simple Tool Example

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get weather for a city."""
    return f"Weather in {city}: 32C and sunny"

print(get_weather.invoke({"city": "Bengaluru"}))
```

## Why Tool Descriptions Matter

Models often choose tools based on descriptions.

Bad description:

- "Handles data"

Good description:

- "Fetch current order status for a given order ID from the order management system"

## Model Bound to Tools

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([get_weather])
```

Now the model can return tool calls instead of only text.

## Typical Agent Loop

```text
User request
   |
   v
LLM decides if tool is needed
   |
   +--> If yes: call tool
   |
   v
LLM receives tool result
   |
   v
Final answer
```

## Good Use Cases for Agents

- support assistants
- workflow assistants
- research assistants
- internal operations copilots

## Bad Use Cases for Agents

- deterministic workflows with fixed steps
- safety-critical side effects without approval
- simple classification or extraction tasks

If the workflow is fixed, use a chain or graph instead of a free agent.

## Example: Tool-Driven Support Assistant

```python
from langchain_core.tools import tool

@tool
def get_order_status(order_id: str) -> str:
    """Fetch order status for a specific order ID."""
    return f"Order {order_id} is shipped and will arrive in 2 days."

@tool
def refund_policy() -> str:
    """Return the company refund policy."""
    return "Refunds are allowed within 7 days for eligible items."
```

A good agent could:

- look up the order first
- consult policy
- then answer the customer

## Common Failure Modes

### 1. Wrong tool chosen

Causes:

- overlapping tool descriptions
- poor system prompt
- ambiguous user request

### 2. Wrong arguments

Causes:

- model extracts incorrect IDs
- schema too weak
- no validation layer

### 3. Infinite or wasteful loops

Causes:

- unclear stop condition
- repeated failed tool attempts
- hallucinated dependencies

### 4. Unsafe side effects

Causes:

- tools allowed to mutate systems directly
- no approval gate
- no auth or role checks

## Production Guardrails

### Validate arguments

Never trust model-generated arguments blindly.

### Separate read tools from write tools

This reduces risk significantly.

### Require confirmation for destructive actions

Examples:

- issuing refund
- deleting record
- changing permissions

### Add retries carefully

Retries without safeguards can amplify cost and side effects.

## Agent vs Chain

This is a very common interview topic.

### Chain

- fixed workflow
- predictable
- easier to test
- easier to optimize

### Agent

- dynamic workflow
- flexible
- harder to test
- harder to bound

Strong answer:

> I prefer chains for deterministic workflows and agents only when dynamic tool selection adds real value. Agents increase flexibility, but they also increase failure modes, so I use them where the decision logic genuinely cannot be hardcoded cleanly.

## Real-World Scenario

Suppose you are building an enterprise support copilot.

Possible tools:

- CRM lookup
- order status
- refund eligibility
- knowledge base search

Good design:

- read-only tools by default
- separate approval for refund actions
- trace every tool call
- evaluate tool selection accuracy

## LangChain and Agent Architecture

LangChain helps with:

- tool definitions
- model-tool binding
- agent orchestration patterns
- integration with tracing

But if the workflow becomes complex and stateful, LangGraph is often a better fit.

## Interview-Worthy Insight

If asked "What is the biggest risk with agents?" a strong answer is:

> The biggest risk is loss of control. Agents can choose the wrong tool, generate invalid arguments, loop unnecessarily, or cause unsafe side effects. That is why I prefer explicit workflows when possible and use validation, confirmations, access controls, and tracing when I do use agents.

## Summary

Tools give capability.
Agents give flexibility.
Flexibility increases risk, so production agents need stronger guardrails than simple chains.
