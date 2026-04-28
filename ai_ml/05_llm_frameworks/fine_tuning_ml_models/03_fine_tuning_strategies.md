# Fine-Tuning Strategies

## The Main Strategy Question

Once you decide fine-tuning is useful, the next question is:

- how much of the model should we update?

This is where strategy matters.

## 1. Full Fine-Tuning

Full fine-tuning updates all model parameters.

### Benefits

- maximum flexibility
- strongest adaptation potential

### Costs

- expensive compute
- large memory requirements
- harder deployment if storing separate full models

### When to use it

- smaller models
- large enough data
- strong need for deep adaptation

## 2. Feature Extraction + Small Head

Common in classical transfer learning.

Idea:

- freeze the pretrained backbone
- train only a classifier head or output layer

Useful for:

- classification tasks
- smaller budgets
- quick baselines

## 3. Layer Freezing / Partial Fine-Tuning

Update only some layers.

Why:

- reduce compute
- preserve general knowledge
- lower overfitting risk

## 4. Supervised Fine-Tuning (SFT)

This is common for LLMs.

Train the model on:

- instruction -> desired response

Goal:

- improve instruction following
- improve style consistency
- improve domain/task adaptation

## 5. Instruction Tuning

A specialized form of supervised fine-tuning where data is formatted as instructions and responses.

Example:

```text
Instruction: Summarize the ticket.
Input: Customer reports duplicate billing for invoice 842.
Output: The customer was charged twice for invoice 842 and needs billing investigation.
```

This teaches the model to follow task instructions better.

## 6. LoRA

LoRA stands for **Low-Rank Adaptation**.

Instead of updating all model weights, it learns small low-rank matrices inserted into the model.

### Why LoRA is popular

- much cheaper than full fine-tuning
- less memory usage
- easy to store and swap adapters

### Interview-worthy intuition

Instead of rewriting the whole model, LoRA learns a compact delta.

## 7. QLoRA

QLoRA combines:

- quantized base model
- LoRA adapters

This allows fine-tuning larger models on smaller hardware.

### Why it matters

- big reduction in memory footprint
- practical for many real teams

## 8. Preference Tuning / Alignment

After supervised fine-tuning, some teams apply preference-based methods to align outputs better with human preferences.

Examples:

- RLHF-style pipelines
- DPO and similar methods

For interviews, know the concept even if you do not go deep into RL math.

## Full Fine-Tuning vs LoRA

This is a highly likely interview question.

### Full Fine-Tuning

- updates all parameters
- expensive
- potentially stronger adaptation

### LoRA

- updates a small subset via adapters
- cheaper
- easier to manage and deploy

Strong answer:

> I would usually start with parameter-efficient tuning like LoRA because it is cheaper and operationally simpler. I would consider full fine-tuning only if the task truly needs deeper adaptation and the expected quality gain justifies the compute and deployment cost.

## Example: LoRA with Hugging Face PEFT

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.1,
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

## Strategy: Start with the Simplest Viable Method

Recommended sequence:

1. prompt baseline
2. prompt + retrieval baseline if needed
3. supervised fine-tuning baseline
4. LoRA / QLoRA if model is large
5. full fine-tuning only if needed

This is a strong senior-level answer because it avoids premature complexity.

## Choosing by Use Case

### Classification on moderate data

- frozen backbone + head
- partial fine-tuning
- full fine-tuning for smaller models

### LLM behavior/style adaptation

- SFT
- instruction tuning
- LoRA / QLoRA

### Large proprietary LLM adaptation

- parameter-efficient tuning usually preferred first

## Common Failure Modes

### 1. Overfitting a small dataset

Cause:

- too many epochs
- too much trainable capacity

### 2. Catastrophic forgetting

Cause:

- narrow or aggressive fine-tuning

### 3. Adapter works offline, deployment is messy

Cause:

- no clear model + adapter version strategy

### 4. Fine-tuning the wrong thing

Cause:

- problem was actually retrieval/freshness, not behavior

## Real-World Problems

### Problem: prompts keep growing to force structure

Fine-tuning may reduce prompt complexity.

### Problem: model is too expensive to fine-tune fully

LoRA or QLoRA may help.

### Problem: multiple customers need slightly different styles

Adapter-based approaches can make per-domain or per-tenant customization easier.

## MANG-Level Interview Insight

If asked "How would you choose a fine-tuning strategy?" a strong answer is:

> I would choose based on task type, data volume, hardware budget, and deployment constraints. For many LLM tasks, I would start with supervised fine-tuning using LoRA or QLoRA because they are cost-efficient and easier to operationalize. I would move to full fine-tuning only if parameter-efficient methods fail to achieve the required quality.

## Summary

The best fine-tuning strategy is usually:

- task-aware
- data-aware
- budget-aware
- simple before complex
