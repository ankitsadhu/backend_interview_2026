# LangSmith Learning Path

LangSmith is the observability, evaluation, debugging, and prompt iteration layer for LLM applications.

This track is designed for interview preparation from basic to advanced, with emphasis on:

- clear fundamentals
- code examples
- production debugging patterns
- real-world failure modes
- interview-style questions and answers

## Contents

1. [Fundamentals](01_fundamentals.md) - what LangSmith is, why it exists, core concepts
2. [Tracing and Instrumentation](02_tracing_and_instrumentation.md) - runs, spans, metadata, callbacks, tracing setup
3. [Evaluation and Experimentation](03_evaluation_and_experimentation.md) - online and offline evals, datasets, human feedback
4. [Debugging and Monitoring](04_debugging_and_monitoring.md) - prompt failures, latency spikes, regressions, root-cause workflows
5. [Production Patterns and Failure Modes](05_production_patterns_and_failures.md) - scaling, cost, privacy, alerting, reliability
6. [Interview Questions](06_interview_questions.md) - MANG-style questions with concise answers

## How to Study

Recommended order:

1. Understand why plain logs are not enough for LLM apps.
2. Learn tracing and how requests become nested runs.
3. Understand evaluation before discussing production quality.
4. Practice debugging scenarios using traces plus user feedback.
5. Finish with system design and interview questions.

## Mental Model

```text
User Request
   |
   v
LLM App / Agent
   |
   +--> Prompt construction
   +--> Retriever / tools / APIs
   +--> Model calls
   +--> Output parsing
   |
   v
LangSmith
   |
   +--> Traces
   +--> Metadata
   +--> Datasets
   +--> Evaluations
   +--> Feedback / annotations
   +--> Monitoring dashboards
```

## Why LangSmith Matters in Interviews

Many candidates can build a demo chatbot. Fewer can explain:

- how to debug a bad answer in production
- how to compare prompt versions safely
- how to trace multi-step agent failures
- how to measure quality beyond "it looks good"
- how to ship LLM systems with observability and guardrails

That is where LangSmith becomes valuable.
