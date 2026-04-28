# Fine-Tuning ML Models Learning Path

This track focuses on **fine-tuning machine learning models**, with special emphasis on **LLM fine-tuning for modern interviews**.

It is designed for interview preparation from basic to advanced, with emphasis on:

- fundamental fine-tuning concepts
- data preparation and dataset quality
- full fine-tuning vs parameter-efficient tuning
- instruction tuning, LoRA, and QLoRA
- evaluation and production tradeoffs
- MANG-style interview questions

## Contents

1. [Fundamentals](01_fundamentals.md) - what fine-tuning is, why it works, when to use it
2. [Data Preparation and Training Setup](02_data_preparation_and_training_setup.md) - dataset design, formatting, train/val/test, tokenization
3. [Fine-Tuning Strategies](03_fine_tuning_strategies.md) - full fine-tuning, transfer learning, LoRA, QLoRA, instruction tuning
4. [Evaluation and Debugging](04_evaluation_and_debugging.md) - metrics, overfitting, ablations, error analysis
5. [Production Patterns and Failure Modes](05_production_patterns_and_failures.md) - deployment, cost, safety, drift, rollback
6. [Interview Questions](06_interview_questions.md) - MANG-style questions with concise answers
7. [LoRA and QLoRA In Depth](07_lora_and_qlora_in_depth.md) - LoRA math intuition, target modules, ranks, quantization, tradeoffs
8. [End-to-End LoRA Training Workflow](08_end_to_end_lora_training_workflow.md) - practical dataset, training, saving adapters, inference
9. [LoRA Production and Interview Deep Dive](09_lora_production_and_interview_deep_dive.md) - deployment patterns, pitfalls, MANG-style answers

## How to Study

Recommended order:

1. Understand what fine-tuning changes in a model.
2. Learn why data quality matters more than many people think.
3. Understand the difference between full fine-tuning and parameter-efficient methods.
4. Learn how to evaluate whether fine-tuning actually helped.
5. Finish with production tradeoffs and interview questions.

## Mental Model

```text
Pretrained Model
  |
  v
Task-specific data
  |
  v
Training / adaptation
  |
  v
Fine-tuned model
  |
  v
Evaluation + deployment + monitoring
```

## Why Fine-Tuning Matters in Interviews

Many candidates say:

- "just fine-tune the model"

Fewer can explain:

- when fine-tuning is the right choice vs prompting or RAG
- how to prepare a good dataset
- how LoRA differs from full fine-tuning
- how to avoid catastrophic forgetting
- how to evaluate gains honestly
- how to operate fine-tuned models safely in production

That is where strong interview performance stands out.
