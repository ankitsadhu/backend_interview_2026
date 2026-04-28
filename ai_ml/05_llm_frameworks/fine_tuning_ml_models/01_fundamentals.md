# Fundamentals

## What is Fine-Tuning?

Fine-tuning means taking a pretrained model and continuing training on a smaller, task-specific dataset so the model adapts to a new task, domain, style, or behavior.

The core idea:

- pretraining gives broad general capability
- fine-tuning specializes the model

## Why Pretrained Models Need Fine-Tuning

A pretrained model may already know a lot, but it may not be optimized for:

- your domain vocabulary
- your task format
- your label space
- your output style
- your policies and constraints

Examples:

- medical text classification
- legal document summarization
- code generation in one company’s internal style
- customer support tone adaptation
- instruction-following behavior

## Fine-Tuning vs Training from Scratch

### Training from scratch

- requires huge data
- requires large compute
- expensive and slow

### Fine-tuning

- reuses pretrained knowledge
- needs much less data
- usually faster and cheaper

This is why fine-tuning is so common in practice.

## Fine-Tuning vs Prompting

A common interview question.

### Prompting

Useful when:

- the model already performs well
- requirements are lightweight
- behavior changes often
- you want fast iteration

### Fine-tuning

Useful when:

- you need consistent output behavior
- task patterns repeat often
- prompts are getting too large or brittle
- latency or token cost from long prompts is too high
- the domain/task gap is meaningful

## Fine-Tuning vs RAG

Another common interview question.

### RAG

Best for:

- up-to-date knowledge
- large external knowledge bases
- grounded retrieval
- frequently changing facts

### Fine-tuning

Best for:

- behavior adaptation
- style adaptation
- task-format learning
- consistent structured outputs
- domain/task specialization

Strong answer:

> RAG teaches the model what to look at at inference time, while fine-tuning changes the model’s behavior or internal task adaptation. If the issue is missing knowledge, I first think about RAG. If the issue is repeated behavior, tone, structure, or task performance, I consider fine-tuning.

## What Changes During Fine-Tuning?

Model weights are updated so the model better predicts outputs for the new task distribution.

Conceptually:

```text
pretrained weights
   +
task-specific gradient updates
   ->
adapted weights
```

## Common Fine-Tuning Goals

### 1. Classification

Examples:

- spam detection
- sentiment analysis
- intent classification

### 2. Generation

Examples:

- summarization
- translation
- answer generation

### 3. Instruction following

Examples:

- better formatting
- stronger task compliance
- better tool-use style

### 4. Domain adaptation

Examples:

- legal documents
- finance reports
- healthcare terminology

## LLM Fine-Tuning Types

For modern interviews, you should know at least these:

- supervised fine-tuning (SFT)
- instruction tuning
- preference tuning / RLHF-style alignment
- LoRA / adapter-based tuning
- QLoRA

## Example: Classification Fine-Tuning Intuition

Suppose a generic language model struggles to classify support tickets.

Fine-tuning with examples like:

```text
Input: "Customer was charged twice"
Label: "billing"

Input: "Package has not arrived"
Label: "shipping"
```

helps the model learn the specific label distribution and phrasing patterns.

## Example: Instruction Fine-Tuning Intuition

Suppose you want consistent structured answers:

```json
{
  "priority": "high",
  "team": "payments",
  "reason": "duplicate charge"
}
```

A fine-tuned model can become much more reliable than prompt-only approaches for this style of output.

## Benefits of Fine-Tuning

- better task performance
- more consistent outputs
- less prompt engineering burden
- lower prompt length at inference
- domain adaptation

## Risks of Fine-Tuning

- overfitting
- catastrophic forgetting
- poor generalization
- expensive experiments
- hidden bias amplification
- training on low-quality data

## Catastrophic Forgetting

This means the model becomes better at the new task but worse at older general capabilities.

This happens when:

- dataset is narrow
- training is too aggressive
- fine-tuning objective is overly specialized

## Real-World Problems It Solves

### Problem: prompt is 2 pages long and still inconsistent

Fine-tuning may reduce prompt dependence.

### Problem: model understands English but not your company’s document style

Domain adaptation may help.

### Problem: structured output keeps breaking downstream systems

Task-specific fine-tuning may improve consistency.

## When Not to Fine-Tune

A strong candidate should say this clearly.

Do not fine-tune just because it sounds advanced.

Avoid it when:

- prompting already works well
- the main issue is factual freshness
- you lack enough good data
- inference-time retrieval would solve the problem better

## MANG-Level Interview Insight

If asked "When would you fine-tune?" a strong answer is:

> I would fine-tune when the problem is repeated task behavior rather than missing external knowledge. For example, if I need consistent instruction following, domain-specific output style, or better performance on a recurring task, fine-tuning can help. But if the issue is fresh knowledge or factual grounding, I would consider RAG first rather than encoding changing facts into weights.

## Summary

Fine-tuning is about specialization.

The real engineering question is not "can we fine-tune?" but "should we fine-tune for this problem?"
