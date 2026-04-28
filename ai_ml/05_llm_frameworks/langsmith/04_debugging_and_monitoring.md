# Debugging and Monitoring

## Why LLM Debugging Feels Different

In normal backend debugging, a bug often maps to a deterministic code path.

In LLM systems, a bad user outcome may come from:

- poor prompt instructions
- wrong retrieved context
- stale embeddings
- wrong tool selection
- parser fragility
- model randomness
- hidden latency from retries

LangSmith helps reduce the search space.

## Debugging Workflow

When a production issue appears, inspect in this order:

1. input and user intent
2. prompt version and model settings
3. retrieval results
4. tool calls and arguments
5. intermediate outputs
6. final answer
7. feedback and similar failing traces

## Example Incident 1: Hallucinated Policy Answer

Symptom:

- assistant confidently answers a compliance question with no source citation

Trace review:

- retriever returned irrelevant chunks
- prompt did not enforce "answer only from context"
- final answer looked fluent but was unsupported

Fix:

- improve retrieval filters
- require citations
- add abstain behavior: "I do not know from available documents"
- create regression eval for policy questions

## Example Incident 2: Agent Calls Wrong Tool

Symptom:

- support bot updates a ticket instead of fetching ticket details

Trace review:

- intent classification ambiguous
- tool descriptions overlapped
- model selected the first matching tool

Fix:

- rewrite tool descriptions
- add tool selection examples
- use stricter router step before tool calling
- add evaluator for expected tool usage

## Example Incident 3: Latency Spike

Symptom:

- P95 latency increased from 3s to 11s

Trace review:

- retriever normal
- first model call normal
- second model call repeated after parser failure
- retry loop triggered twice

Fix:

- make parser more robust
- limit retries
- add alert on repeated parser-retry traces

## Monitoring Dimensions

You should monitor more than accuracy.

### Quality

- success rate
- groundedness
- user thumbs up/down
- escalation rate

### Performance

- P50 / P95 / P99 latency
- tokens in / out
- tool latency
- queue delay

### Reliability

- model timeout rate
- parser failure rate
- tool failure rate
- fallback activation rate

### Cost

- cost per request
- cost per tenant
- cost per endpoint
- expensive trace patterns

## Signals Worth Alerting On

Examples:

- hallucination reports increased 3x week over week
- parser failure rate > 2%
- average prompt tokens jumped 40%
- retrieval returned zero docs for top workflow
- model fallback usage suddenly increased

Alerting only on infra metrics is not enough for LLM systems.

## Practical Metadata for Monitoring

Tag traces with:

- `env=prod`
- `prompt_version=v12`
- `feature=claims-agent`
- `tenant=enterprise`
- `release=2026-04-28`

This lets you answer:

- did the issue begin after a deploy?
- is only one tenant affected?
- did one prompt version regress?

## Redaction and Privacy

Production traces may contain:

- customer names
- support ticket text
- internal documents
- legal or financial content

Best practices:

- mask PII before sending trace payloads
- avoid raw secrets in prompts
- store document IDs instead of full sensitive documents when possible
- restrict access by environment and role

## Example: Structured Monitoring Record

```python
trace_metadata = {
    "tenant_id": "acme-corp",
    "prompt_version": "policy-v7",
    "model": "gpt-4o-mini",
    "retrieval_top_k": 5,
    "release": "2026-04-28.1",
}
```

This metadata matters when you need to slice failures.

## Common Root Causes in Real Systems

### Retrieval bugs

- embeddings not refreshed
- wrong namespace or tenant filter
- chunking destroys meaning
- top-k too low

### Prompt bugs

- instruction order weak
- examples outdated
- conflict between system and tool messages
- no abstain path

### Tooling bugs

- unclear tool schema
- poor tool descriptions
- side-effectful tools invoked without confirmation
- missing idempotency in retries

### Output parsing bugs

- model returns near-valid JSON
- missing field breaks parser
- downstream code assumes strict structure

## Playbook for Regression After Prompt Change

1. Compare traces before and after release.
2. Filter by `prompt_version`.
3. Run dataset eval on the old and new prompt.
4. Inspect failure clusters:
   - hallucination
   - over-refusal
   - format errors
   - latency increase
5. Roll back or gate rollout if quality drops.

## MANG-Style Discussion Point

If asked "How do you debug an LLM app in production?" do not answer with only "I look at logs."

A better answer:

> I would inspect the end-to-end trace, because LLM failures can come from retrieval, prompt construction, tool invocation, parsing, or the model itself. I would slice traces by release and prompt version, compare successful and failing runs, and then add targeted evaluations so the same failure becomes a regression test.

## Summary

Debugging LLM apps is about narrowing uncertainty.

LangSmith helps you map a user complaint to a concrete failing step and then convert that failure into a measurable monitoring signal or regression test.
