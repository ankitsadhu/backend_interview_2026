# Production Patterns and Failure Modes

## The Production Mindset

A demo proves the app can work once.

Production requires:

- predictable workflows
- observability
- evaluation
- safe rollout
- latency control
- cost control
- privacy

LangChain helps structure code, but it does not solve production reliability by itself.

## Pattern 1: Start Simple

Do not begin with agents unless necessary.

Recommended maturity path:

1. prompt + model
2. prompt + model + parser
3. retrieval pipeline
4. fixed chain with validation
5. agent only if dynamic decisions are required

This is a strong interview answer because it shows engineering discipline.

## Pattern 2: Version Prompts and Chains

You should version:

- prompts
- chain logic
- retrieval settings
- model versions

Otherwise regressions become difficult to diagnose.

## Pattern 3: Use Structured Outputs for Backend Flows

If a downstream system expects fields, do not rely on free-form text.

Prefer:

- schema-bound outputs
- validators
- fallback behavior when parsing fails

## Pattern 4: Control Context Size

Large prompts often lead to:

- higher cost
- slower latency
- more irrelevant noise

Mitigations:

- better chunking
- reranking
- top-k tuning
- prompt compression

## Pattern 5: Keep Side Effects Behind Guardrails

For write actions:

- validate arguments
- require confirmation
- enforce auth checks
- use idempotency keys
- log tool actions separately

## Common Production Problems

### 1. Spaghetti chains

Symptoms:

- too many nested runnables
- hard-to-read custom lambdas
- unclear ownership

Fix:

- split into named reusable subchains
- move business logic into normal Python where clearer

### 2. Retrieval quality collapse

Symptoms:

- answers become generic or wrong

Causes:

- stale index
- bad chunking
- no metadata filters
- wrong embedding model

### 3. Token and cost explosion

Symptoms:

- costs jump after release

Causes:

- huge context windows
- repeated retries
- verbose prompts
- unnecessary multi-step chains

### 4. Latency creep

Symptoms:

- no outage, but user satisfaction drops

Causes:

- sequential tool calls
- overuse of large models
- slow retrievers
- fragile parsing causing retries

### 5. Agent instability

Symptoms:

- wrong tool usage
- unnecessary loops
- inconsistent answers

Causes:

- weak prompts
- too many similar tools
- no step limits
- no validation

## Real-World Scenario: Resume Screening Assistant

Workflow:

- parse resume
- extract structured fields
- match against job description
- generate summary

Good LangChain fit:

- prompt templates
- structured output
- fixed pipeline

Bad LangChain fit:

- using a free-form agent for a deterministic extraction pipeline

## Real-World Scenario: Internal Docs Assistant

Workflow:

- retrieve docs
- filter by tenant/product
- generate answer with citations

Main risks:

- stale docs
- poor retrieval
- cross-tenant leakage
- unsupported answers without citations

## Real-World Scenario: Ops Copilot

Workflow:

- read dashboards
- query logs
- summarize incident
- optionally suggest remediation

Main risks:

- wrong metric interpretation
- hidden tool errors
- overconfident recommendations

## When to Prefer Custom Code Over LangChain

This is an important senior-level point.

Prefer custom code when:

- workflow is simple and direct
- framework abstractions add confusion
- you need precise control over retries and state
- debugging framework internals costs more than hand-written orchestration

Strong answer:

> I use LangChain when the abstractions improve clarity and reuse, especially for prompts, retrieval, and structured composition. If the workflow is simple or highly custom, I would prefer plain Python plus provider SDKs because fewer abstractions can be easier to reason about and operate.

## What Interviewers Like to Hear

They like candidates who understand:

- chains before agents
- retrieval quality before model hype
- structured outputs before downstream integration
- observability and evaluation before production rollout

## Summary

LangChain is a useful orchestration layer, but production excellence still depends on design discipline.

The best systems are usually:

- explicit
- observable
- evaluated
- bounded
