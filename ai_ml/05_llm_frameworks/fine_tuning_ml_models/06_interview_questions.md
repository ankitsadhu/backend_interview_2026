# Interview Questions

## 1. What is fine-tuning?

Fine-tuning is the process of taking a pretrained model and continuing training on task-specific data so that it adapts to a new task, domain, style, or behavior.

## 2. Why fine-tune instead of train from scratch?

Because pretraining is expensive and data-hungry, while fine-tuning reuses existing model knowledge and usually requires much less data and compute.

## 3. When should you fine-tune instead of prompt?

I would fine-tune when I need more consistent behavior, stronger domain adaptation, better task performance, or reduced prompt complexity. If prompting already works well, I would avoid fine-tuning.

## 4. When should you use RAG instead of fine-tuning?

I would use RAG when the problem is current or external knowledge rather than behavior adaptation. Fine-tuning is better for style, structure, and repeated task patterns; RAG is better for fresh grounded knowledge.

## 5. What is catastrophic forgetting?

It is when a model becomes better at the fine-tuned task but loses some of its broader general capability or prior behavior.

## 6. Why is data quality so important in fine-tuning?

Because noisy, inconsistent, or unrepresentative data leads to poor generalization, unstable outputs, and misleading evaluation no matter how sophisticated the training method is.

## 7. What is supervised fine-tuning?

Supervised fine-tuning trains the model on labeled input-output examples so it learns to produce the desired target behavior.

## 8. What is instruction tuning?

Instruction tuning is a form of supervised fine-tuning where the model is trained on instruction-response examples to improve instruction following.

## 9. What is LoRA?

LoRA is a parameter-efficient fine-tuning method that learns small low-rank adapter updates instead of modifying all model weights.

## 10. What is QLoRA?

QLoRA combines quantization of the base model with LoRA adapters so larger models can be fine-tuned using much less memory.

## 11. Full fine-tuning or LoRA: which would you choose?

I would usually start with LoRA or QLoRA for large models because they are cheaper and easier to operationalize. I would consider full fine-tuning only if the quality gains justify the added cost and complexity.

## 12. How would you split the dataset?

Into train, validation, and test sets, making sure there is no leakage or near-duplicate contamination across splits.

## 13. What metrics would you use to evaluate a fine-tuned model?

It depends on the task:

- classification: accuracy, precision, recall, F1
- generation: task-specific quality, format compliance, factuality, human review
- LLM tasks: task success, schema correctness, safety, latency, and business metrics

## 14. How do you know if fine-tuning actually helped?

By comparing against strong baselines, analyzing failure cases, checking held-out evaluation results, and validating behavior on realistic production-like data.

## 15. What are common failure modes in fine-tuning?

- overfitting
- catastrophic forgetting
- poor dataset quality
- benchmark mismatch
- stale knowledge encoded into weights
- deployment/version confusion

## 16. How would you make a fine-tuned model production-ready?

I would version data and models, keep strong baselines, roll out gradually, monitor drift and safety, and maintain a rollback path.

## 17. Can fine-tuning replace retrieval?

Usually no. Fine-tuning is poor for frequently changing facts. Retrieval is better for current external knowledge.

## 18. What is the strongest one-line explanation of fine-tuning?

Fine-tuning specializes a pretrained model for a narrower task or behavior without paying the full cost of training a model from scratch.

## Rapid-Fire Answers

### Is lower training loss enough to claim success?

No. You need validation, realistic benchmarks, and task-aligned evaluation.

### What matters more, clever training tricks or good data?

Usually good data.

### Should every LLM product be fine-tuned?

No. Many can be solved with prompting, retrieval, tools, or workflow design.

### Why are LoRA-style methods popular?

Because they reduce memory and compute cost while keeping good adaptation quality.

### What is the biggest mistake teams make?

Fine-tuning before proving that prompting, retrieval, and simpler baselines are insufficient.

## Final Interview Tip

For fine-tuning interviews, always connect:

1. when to fine-tune
2. data quality
3. strategy choice
4. evaluation and production tradeoffs

That makes the answer sound senior and practical rather than just theoretical.
