# LangGraph Interview Questions

## 1. What is LangGraph?

LangGraph is a framework for building stateful, graph-based LLM workflows where execution moves through nodes and edges over shared state.

## 2. Why do we need LangGraph if we already have LangChain?

LangChain provides reusable LLM building blocks such as prompts, models, retrievers, parsers, and tools. LangGraph is useful when the workflow becomes stateful and non-linear, such as branching, looping, retries, approval steps, or durable execution.

## 3. What is the difference between LangChain and LangGraph?

- LangChain focuses on composable components and pipelines.
- LangGraph focuses on explicit workflow control over shared state.

They are complementary, not competing tools.

## 4. What is state in LangGraph?

State is the shared data object that flows through the graph and gets updated by nodes. It can include user input, retrieved documents, tool results, retry counters, approval status, and final output.

## 5. What is a node?

A node is a processing step in the workflow, such as classify intent, retrieve documents, call a tool, validate an output, or ask for human approval.

## 6. What is an edge?

An edge determines which node runs next. It can be linear, conditional, or part of a loop.

## 7. When should you use LangGraph?

I would use LangGraph when the workflow needs explicit state, branching, loops, retries, human-in-the-loop approval, or resumability.

## 8. When should you not use LangGraph?

I would avoid it for simple pipelines where a chain or plain code is clearer. If the workflow is basically prompt -> model -> parser, LangGraph is usually unnecessary.

## 9. Why is LangGraph good for agent systems?

Because it makes the agent loop explicit. That allows bounded iterations, validation nodes, failure routing, human approvals, and safer tool orchestration.

## 10. What are common LangGraph use cases?

- support assistants with approvals
- research assistants with iterative retrieval
- workflow copilots with branching logic
- ops agents with controlled remediation
- long-running LLM workflows

## 11. What are common failure modes in LangGraph systems?

- messy state design
- unbounded loops
- retry storms
- duplicate side effects on resume
- approval bottlenecks
- too many unclear nodes

## 12. How would you make a LangGraph workflow production-ready?

I would use typed state, explicit routing, bounded loops, checkpointing, idempotency for side effects, observability per node, evaluation for key paths, and human approval for risky actions.

## 13. What is durable execution?

Durable execution means the workflow can persist progress, survive restarts, pause, and resume later from saved state or checkpoints.

## 14. Why is durable execution important?

Because many real workflows are long-running, depend on external systems, or wait for human input. Without durability, failures can cause lost progress or duplicated work.

## 15. Why is human-in-the-loop important?

Because some decisions have enough business, legal, financial, or operational risk that they should not be fully autonomous.

## 16. What is the biggest risk with graph-based agents?

The biggest risk is poorly controlled complexity. If the graph has messy state, weak route logic, and unbounded loops, it becomes hard to reason about and unsafe in production.

## 17. How would you compare a chain, an agent, and a graph?

- A chain is fixed and predictable.
- An agent is dynamic and flexible.
- A graph is an explicit workflow model that can contain fixed steps, agent loops, validation, and human checkpoints.

## 18. What is a strong one-line description of LangGraph?

LangGraph is a workflow orchestration framework for building stateful, controllable LLM systems with explicit transitions, loops, and recovery paths.

## Rapid-Fire Answers

### Does LangGraph replace LangChain?

No. LangGraph often uses LangChain components inside graph nodes.

### Is LangGraph only for autonomous agents?

No. It is useful for any workflow that benefits from explicit state and routing.

### What matters most for maintainability?

Clean state design and clear node responsibilities.

### What matters most for safety?

Bounded loops, validated tool use, approval gates, and idempotent side effects.

### What matters most for reliability?

Checkpointing, explicit failure paths, observability, and resumability.

## Final Interview Tip

For LangGraph interviews, always connect:

1. stateful workflow design
2. explicit control flow
3. bounded autonomy
4. production-safe execution

That is what makes the answer sound senior and practical.
