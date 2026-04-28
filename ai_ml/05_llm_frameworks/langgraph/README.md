# LangGraph Learning Path

LangGraph is a framework for building **stateful, controllable, graph-based LLM workflows**.

It is especially useful when your application needs:

- explicit workflow state
- branching logic
- retries
- loops
- tool-use cycles
- human-in-the-loop checkpoints
- durable execution

This track is designed for interview preparation from basic to advanced, with emphasis on:

- clear fundamentals
- graph-based mental models
- code examples
- agent workflow design
- production failure modes
- interview-style questions and answers

## Contents

1. [Fundamentals](01_fundamentals.md) - what LangGraph is, why it exists, where it fits
2. [State, Nodes, and Edges](02_state_nodes_and_edges.md) - graph structure, typed state, control flow
3. [Building Workflows and Agent Loops](03_workflows_and_agent_loops.md) - conditional routing, tool loops, retries, handoffs
4. [Human-in-the-Loop and Durable Execution](04_human_in_the_loop_and_durable_execution.md) - checkpoints, approvals, resumability
5. [Production Patterns and Failure Modes](05_production_patterns_and_failures.md) - observability, safety, cost, latency, recovery
6. [Interview Questions](06_interview_questions.md) - MANG-style questions with concise answers

## How to Study

Recommended order:

1. Understand why chains are not enough for some workflows.
2. Learn the graph mental model: state, nodes, edges.
3. Study agent loops and conditional routing.
4. Learn human approval and durable execution patterns.
5. Finish with production tradeoffs and interview questions.

## Mental Model

```text
Request
  |
  v
State Graph
  |
  +--> Node: classify
  +--> Node: retrieve
  +--> Node: tool_call
  +--> Node: validate
  +--> Node: ask_human
  +--> Node: finalize
  |
  v
Controlled Outcome
```

## Why LangGraph Matters in Interviews

Many candidates can explain prompts and chains.

Fewer can explain:

- how to build stateful agent workflows
- how to handle retries and branching cleanly
- how to pause for human approval
- how to resume long-running flows safely
- how to keep agent systems controllable in production

That is where LangGraph becomes valuable.
