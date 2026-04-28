# Evaluation and Debugging

## Why Evaluation Matters

A common mistake is:

- train model
- see lower loss
- assume success

Lower training loss does not guarantee:

- better business performance
- better generalization
- safer outputs

## What to Measure

Depends on the task.

### Classification

- accuracy
- precision
- recall
- F1
- per-class metrics

### Generation / summarization

- ROUGE / BLEU style metrics
- factuality
- helpfulness
- format compliance
- human evaluation

### LLM instruction tasks

- task success rate
- schema correctness
- refusal quality
- hallucination rate
- latency and cost

## Validation Loss vs Real Quality

Validation loss is useful but incomplete.

Why:

- it may not capture business-specific success
- generative quality is often multi-dimensional
- format correctness may matter more than token-level similarity

## Error Analysis

A strong candidate always mentions this.

Do not just look at aggregate metrics.

Slice by:

- class
- language
- customer segment
- input length
- domain subtype
- failure category

## Example: Classification Metrics with scikit-learn

```python
from sklearn.metrics import classification_report

y_true = ["billing", "shipping", "billing", "fraud"]
y_pred = ["billing", "shipping", "support", "fraud"]

print(classification_report(y_true, y_pred))
```

## Example: Generative Evaluation Mindset

Suppose a summarization model produces fluent but incomplete outputs.

You should check:

- missing key facts
- hallucinated details
- formatting errors
- domain-specific omissions

This is why human review often still matters.

## Overfitting

Symptoms:

- training loss keeps improving
- validation performance worsens
- production behavior becomes brittle

Fixes:

- fewer epochs
- lower learning rate
- more or better data
- regularization
- early stopping

## Underfitting

Symptoms:

- both training and validation performance remain weak

Possible causes:

- insufficient training
- model too small
- poor data quality
- task not represented well

## Catastrophic Forgetting Detection

After fine-tuning, compare:

- original benchmark capability
- new task capability

If the model got better on the target task but much worse elsewhere, you may have over-specialized it.

## Ablation Studies

An interviewer may ask how to know what actually helped.

Use ablations:

- base model vs tuned model
- prompt baseline vs tuned model
- LoRA vs full fine-tuning
- old dataset vs cleaned dataset
- with and without retrieval

This avoids fake confidence.

## Debugging Workflow

When the fine-tuned model underperforms:

1. inspect data quality
2. verify train/validation split
3. check formatting consistency
4. compare against prompt-only baseline
5. analyze failure clusters
6. tune hyperparameters only after data sanity

## Example Failure Patterns

### Problem: model output schema breaks randomly

Cause:

- target outputs inconsistent
- evaluation ignores format compliance

### Problem: minority class performance is terrible

Cause:

- class imbalance
- not enough rare examples

### Problem: model is fluent but wrong

Cause:

- style learned better than correctness
- evaluation metric not aligned with factuality

## Evaluation for LLM Fine-Tuning

For modern LLM fine-tuning, a good evaluation setup often combines:

- automatic task metrics
- schema or rule-based checks
- LLM-as-judge carefully used
- human review on critical slices

## Offline vs Online Evaluation

### Offline

Used before deployment.

### Online

Used after deployment.

Examples:

- user acceptance
- fallback rate
- correction rate
- latency
- escalation rate

## Real-World Problems

### Problem: offline metrics improve, users complain more

Cause:

- benchmark mismatch
- evaluation ignores UX or latency

### Problem: test set score great, new customer data poor

Cause:

- split leakage or narrow dataset

### Problem: evaluation rewards verbosity instead of precision

Cause:

- metric poorly aligned with business goal

## MANG-Level Interview Insight

If asked "How would you evaluate a fine-tuned model?" a strong answer is:

> I would start with task-appropriate offline metrics, but I would not stop there. I would compare against a strong baseline, inspect slices and failure modes, and make sure the evaluation reflects real business behavior, not just lower validation loss. For LLMs, I would usually combine rule-based checks, targeted human review, and production signals after rollout.

## Summary

Evaluation is what separates:

- real improvement
- from optimistic overfitting
