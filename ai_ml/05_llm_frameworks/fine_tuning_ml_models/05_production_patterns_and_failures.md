# Production Patterns and Failure Modes

## The Production Mindset

Training a better model is only half the problem.

Production requires:

- reproducibility
- versioning
- rollback
- safety
- drift monitoring
- cost control

Many teams fail here, not during training.

## Pattern 1: Treat Data and Model as Versioned Artifacts

Track:

- dataset version
- preprocessing version
- base model version
- tuning method
- hyperparameters
- evaluation results

Without this, debugging regressions becomes painful.

## Pattern 2: Always Keep a Strong Baseline

Compare against:

- base model
- prompt-engineered baseline
- RAG baseline if relevant

Strong answer:

> A fine-tuned model should beat a realistic baseline, not just a weak baseline.

## Pattern 3: Roll Out Safely

Do not switch all traffic immediately.

Use:

- shadow evaluation
- canary rollout
- A/B testing
- feature flags

## Pattern 4: Monitor Drift

Even a well-tuned model degrades if input distributions change.

Drift sources:

- new customer behavior
- new document formats
- policy changes
- new product lines

## Pattern 5: Keep Inference Practical

A model that is great offline but too slow or too expensive is not a good production model.

Watch:

- latency
- throughput
- GPU / CPU cost
- memory footprint
- batch efficiency

## Pattern 6: Fine-Tuning Does Not Remove Safety Needs

Risks remain:

- hallucination
- toxic outputs
- biased behavior
- policy violations

You may still need:

- guardrails
- output filters
- retrieval grounding
- human review for high-risk tasks

## Common Production Problems

### 1. Offline win, online loss

Symptoms:

- benchmark improved
- user satisfaction dropped

Cause:

- bad benchmark alignment
- overfitting to offline evals

### 2. Model drift

Symptoms:

- quality slowly drops over time

Cause:

- data distribution shifted

### 3. Catastrophic forgetting in production

Symptoms:

- target task improves
- general reliability worsens

### 4. Deployment complexity with multiple adapters

Symptoms:

- confusion about which adapter is active
- inconsistent outputs across environments

### 5. Fine-tuning encoded stale knowledge

Symptoms:

- answers reflect old policy or outdated facts

Cause:

- using fine-tuning for dynamic knowledge instead of retrieval

## Fine-Tuning and RAG Together

This is a strong interview topic.

Often the best system is not:

- only fine-tuning
- only RAG

but a combination:

- fine-tune for behavior, format, domain style
- use RAG for current knowledge and grounding

## Real-World Scenario: Customer Support Assistant

Fine-tuning can help with:

- response tone
- ticket classification
- structured summaries

RAG can help with:

- latest refund policy
- product-specific docs
- account-specific info

## Real-World Scenario: Code Assistant

Fine-tuning can help with:

- code style
- repo-specific patterns
- structured issue summaries

But current codebase knowledge is often better handled via retrieval and tools.

## Real-World Scenario: Enterprise Document Assistant

Do not fine-tune the model to memorize dynamic internal documents.

Prefer:

- RAG for documents
- fine-tuning for answer style and format consistency

## What Interviewers Want to Hear

They want to see that you understand:

- fine-tuning is not automatically the best lever
- data and evaluation are more important than hype
- rollout and rollback matter
- drift and safety must be monitored
- RAG and fine-tuning often complement each other

## Strong Interview Answer

> In production I would treat fine-tuning as part of a larger ML system, not as a one-time training step. I would version data and models, compare against strong baselines, roll out gradually, monitor drift and safety, and combine fine-tuning with retrieval when factual freshness matters. Fine-tuning should improve behavior or task specialization, but it should not be used as a shortcut for missing observability or missing knowledge infrastructure.

## Summary

Production fine-tuning is about:

- disciplined experimentation
- safe deployment
- continuous evaluation
- knowing what not to encode into weights
