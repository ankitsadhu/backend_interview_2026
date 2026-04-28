# LangSmith Interview Questions

## 1. What is LangSmith?

LangSmith is an observability, evaluation, and debugging platform for LLM applications. It helps trace workflows, inspect prompts and tool calls, compare experiments, attach feedback, and monitor quality in production.

## 2. Why do we need LangSmith if we already have logs and APM?

Traditional logs and APM help with deterministic systems, infra health, and exceptions. LangSmith adds LLM-specific visibility:

- prompts
- model inputs and outputs
- retrieval steps
- tool calls
- nested workflow traces
- dataset-driven evaluation

## 3. What is the difference between a run and a trace?

- A **run** is one execution unit, like one model call or retriever call.
- A **trace** is the full tree of nested runs for a request.

## 4. How would you debug a hallucination using LangSmith?

I would inspect the trace and check:

1. what documents were retrieved
2. whether retrieval was relevant and fresh
3. whether the prompt forced grounded answering
4. whether the model ignored context
5. whether output validation or citations were missing

Then I would turn that failure into a regression evaluation case.

## 5. How would you evaluate an LLM system?

I would build a representative dataset from production traffic and failure cases, define metrics such as correctness, groundedness, tool accuracy, latency, and cost, and run offline experiments for prompt or model changes. For critical flows I would combine deterministic checks, LLM judges, and human review.

## 6. What are common metrics to monitor in LangSmith?

- success rate
- latency percentiles
- token usage
- tool failure rate
- parser failure rate
- user feedback score
- groundedness or factuality score
- cost per request

## 7. How does LangSmith help with prompt engineering?

It allows prompt versions to be compared on the same dataset, with trace-level visibility into outputs, latency, and failures. This makes prompt iteration measurable instead of subjective.

## 8. How would you use LangSmith in a RAG system?

I would trace retrieval plus generation, capture retrieved document IDs and scores, evaluate groundedness and citation quality, and monitor empty retrievals, stale content, and hallucination feedback.

## 9. What are common production issues in LLM applications?

- hallucinations
- stale retrieval
- slow tool calls
- parser failures
- cost spikes
- prompt regressions
- wrong tool usage
- privacy leaks in prompts or traces

## 10. How would you reduce incident resolution time for an LLM app?

I would make traces searchable by metadata such as release, prompt version, tenant, and endpoint. Then I would create dashboards and alerts for quality, latency, and tool failure signals. This lets on-call engineers move from "user says it failed" to the exact failing step quickly.

## 11. What is a strong rollout strategy for prompt or model changes?

Use offline evals first, then canary or shadow rollout, compare traces and metrics by cohort, and keep a rollback path. Never ship large prompt or model changes blindly to all traffic.

## 12. What are the limitations of LLM-as-judge evaluation?

- judge model can be biased
- grading can drift across versions
- some tasks are too subjective
- judge prompts themselves need validation

So it should be combined with heuristics and human review for important workflows.

## 13. How would you instrument a custom Python workflow?

I would wrap meaningful steps with tracing decorators or explicit trace calls, capture metadata like tenant, prompt version, and release, and ensure each major operation such as retrieval, tool use, and generation becomes a visible run in the trace tree.

## 14. What is the most important difference between demo-grade and production-grade LLM systems?

Production-grade systems have:

- observability
- repeatable evaluation
- versioning
- safe rollouts
- privacy controls
- incident response workflows

Demo systems usually only show that a happy path works once.

## 15. How would you answer "Where does LangSmith fit in the stack?"

LangSmith sits in the observability and evaluation layer of the LLM stack. The app still uses normal backend components like APIs, queues, databases, and metrics systems, but LangSmith gives workflow-level visibility into prompts, runs, tools, and evaluations.

## Short Rapid-Fire Answers

### Is LangSmith only for LangChain?

No. It is strongest in that ecosystem, but custom workflows can also be instrumented.

### Does tracing replace evaluation?

No. Tracing explains behavior. Evaluation measures quality.

### Is one global accuracy score enough?

No. Slice by workflow, tenant, language, or query type because regressions are often segment-specific.

### What metadata is most useful?

Prompt version, model, release version, tenant, feature, session, and experiment tag.

### What should happen after a major incident?

The failing traces should become evaluation examples so the bug is less likely to recur.

## Final Interview Tip

When answering LangSmith questions, always connect four themes:

1. observability
2. evaluation
3. production reliability
4. continuous improvement from real failures

That is the level that stands out in strong interviews.
