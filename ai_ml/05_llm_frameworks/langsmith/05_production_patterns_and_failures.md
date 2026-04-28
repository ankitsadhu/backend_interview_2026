# Production Patterns and Failure Modes

## The Real Production Question

A beginner asks:

- "How do I trace my chain?"

A strong interview candidate asks:

- "How do I make this observable, reliable, safe, and cost-efficient under real traffic?"

That is the production mindset.

## Reference Architecture

```text
Client
  |
API / Gateway
  |
LLM Orchestrator
  |
  +--> Prompt builder
  +--> Retriever / vector DB
  +--> Tools / internal APIs
  +--> LLM provider
  +--> Output validator
  |
LangSmith
  +--> traces
  +--> evals
  +--> feedback
  +--> experiment comparison
```

## Production Patterns

### 1. Prompt Versioning

Always track prompt versions explicitly.

Do not rely on:

- "I think this is the latest prompt"
- hidden prompt changes in code

Track:

- prompt ID
- version
- release date
- experiment cohort

This makes regressions debuggable.

### 2. Safe Rollouts

Do not ship major prompt or model changes to 100% traffic immediately.

Use:

- canary rollout
- shadow evaluation
- tenant-based gradual rollout
- internal-only traffic first

### 3. Fallback Models

If the primary provider times out or rate-limits, use a fallback.

But track fallback activation carefully because:

- quality may differ
- cost may change
- response style may drift

### 4. Human-in-the-Loop for High Risk Actions

For workflows like:

- refunds
- legal drafting
- medical assistance
- permission changes

use human approval or confirmation steps.

### 5. Trace-Driven Postmortems

Every major incident should produce:

- root cause trace examples
- new evaluation cases
- new alerts or dashboards

Otherwise the same bug returns.

## Failure Mode: Cost Explosion

Symptoms:

- token costs double after a release

Possible causes:

- larger retrieved context
- extra reasoning step
- repeated retries
- longer system prompts
- model switched to premium tier

How LangSmith helps:

- compare token usage by trace step
- compare prompt versions
- identify workflows with token spikes

Mitigations:

- trim context
- compress documents
- cap retries
- use cheaper model for simpler steps

## Failure Mode: Latency Creep

Symptoms:

- user complaints increase, but no hard outage

Possible causes:

- tool latency increased
- model provider degraded
- too many chained calls
- retries on malformed output

Mitigations:

- enforce latency budgets per stage
- parallelize independent tool calls
- use smaller model for routing/classification
- set timeouts and fallbacks

## Failure Mode: Silent Quality Regression

Symptoms:

- system still returns answers, but trust drops

Possible causes:

- prompt tone changed
- retriever index stale
- new model less grounded
- business policy changed but dataset was not refreshed

Mitigations:

- benchmark on production-like datasets
- collect targeted user feedback
- maintain holdout regression suites
- inspect slices, not just overall averages

## Failure Mode: Privacy Leakage

Symptoms:

- sensitive data appears in traces or model prompts

Risks:

- compliance violations
- insider data exposure
- accidental retention of secrets

Mitigations:

- redact PII before tracing
- separate sensitive workloads
- minimize payload retention
- use access controls and audit trails

## Failure Mode: Tool Abuse or Side Effects

If the model can call tools like:

- refund payment
- delete file
- change permissions

then tracing alone is not enough.

Need:

- confirmation gates
- idempotency keys
- role checks
- side-effect audit logs
- allowlists for tool execution

## Real-World Scenario: Customer Support Agent

Suppose you run an LLM assistant for support.

Production goals:

- reduce tickets
- maintain factual accuracy
- keep average latency under 4s
- avoid refund mistakes

Useful LangSmith setup:

- traces tagged by tenant and issue type
- dataset of past support tickets
- tool correctness eval for order lookup / refund action
- dashboards for hallucination feedback and escalation rate

Likely failure cases:

- wrong tool parameters
- stale order status
- unsupported refund promise
- slow downstream CRM API

## Real-World Scenario: Enterprise RAG Assistant

Production goals:

- grounded answers
- citations
- no cross-tenant leaks
- document freshness

Useful LangSmith setup:

- metadata with tenant ID and document version
- evals for citation correctness
- alerts when retrieval returns empty or cross-tenant results
- comparison between embedding versions

Likely failure cases:

- stale index
- weak tenant filters
- chunking issues
- model answers from prior knowledge instead of source docs

## What Senior Interviewers Want

They want to see that you understand:

- observability is not enough without evaluation
- evaluation is not enough without production feedback
- trace data must be searchable and privacy-aware
- releases need controlled rollout and rollback paths
- incidents should generate new regression tests

## Strong Interview Answer

> In production I would use LangSmith as the observability and evaluation layer for the LLM workflow. I would version prompts, tag traces with release and tenant metadata, run offline evals before rollout, canary large changes, and monitor quality, latency, and cost together. For high-risk actions I would add approval gates and strict tool controls. After incidents, I would turn failing traces into regression datasets so the system improves over time instead of just being patched once.

## Summary

Production excellence with LLM systems is not about one clever prompt.

It is about repeatability, visibility, feedback loops, and controlled change management.
