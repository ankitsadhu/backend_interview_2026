# LoRA and QLoRA In Depth

## Why LoRA Became So Popular

Full fine-tuning of large language models is expensive because:

- all parameters are updated
- optimizer state is large
- GPU memory usage is high
- each tuned model becomes a full copy

LoRA became popular because it keeps the base model mostly frozen and learns a much smaller set of trainable parameters.

## Core LoRA Idea

Instead of directly updating a large weight matrix `W`, LoRA learns a low-rank update:

```text
W' = W + DeltaW

DeltaW ≈ A x B
```

Where:

- `W` is the original frozen weight matrix
- `A` and `B` are much smaller trainable matrices
- rank `r` controls the size of the update

This means the model learns a compact adaptation rather than rewriting the whole model.

## Intuition

If full fine-tuning says:

- "let me change everything"

LoRA says:

- "let me learn a small but useful correction"

That is why LoRA is often much cheaper while still performing well.

## Why Low Rank Helps

The assumption behind LoRA is that task-specific adaptation often lies in a lower-dimensional subspace.

So instead of updating a huge matrix directly, we can approximate the useful update with a low-rank factorization.

This is the key interview intuition. You do not need deep linear algebra to explain it well.

## Where LoRA is Applied

In transformers, LoRA is commonly applied to attention and projection layers.

Typical target modules:

- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`
- sometimes MLP projection layers

The exact module names depend on the model family.

## Important LoRA Hyperparameters

### `r` (rank)

Controls the size of the low-rank adaptation.

- smaller `r` -> fewer trainable params, cheaper, less expressive
- larger `r` -> more expressive, more memory, more risk of overfitting

### `lora_alpha`

Scaling factor for the LoRA update.

Think of it as controlling the strength of the learned adapter contribution.

### `lora_dropout`

Dropout applied on LoRA paths to help regularization.

### `target_modules`

Specifies which submodules receive LoRA adapters.

This matters a lot in practice.

## Example LoRA Configuration

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "v_proj"],
)
```

## Trainable Parameter Savings

One of the strongest selling points of LoRA is the dramatic reduction in trainable parameters.

Typical result:

- base model: billions of frozen parameters
- trainable adapter params: tiny fraction of total

This reduces:

- optimizer memory
- checkpoint size
- training cost

## LoRA vs Adapters

Broadly speaking, LoRA is one type of parameter-efficient fine-tuning.

Compared with classic adapter layers:

- LoRA is lightweight
- often easier to integrate
- has become very common for LLM tuning

## What is QLoRA?

QLoRA combines:

- a quantized base model
- LoRA adapters trained on top

The base model is usually loaded in low-bit form, while the adapter weights remain trainable.

## Why QLoRA Matters

Many teams want to fine-tune large models but do not have huge GPU clusters.

QLoRA makes this more practical by reducing memory usage significantly.

That is why it is very interview-relevant.

## QLoRA Intuition

QLoRA says:

- keep the large frozen model compressed
- train only small LoRA adapters

So we get:

- lower memory footprint
- ability to tune larger models on smaller hardware

## Example QLoRA Loading Pattern

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype="bfloat16",
)

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    quantization_config=bnb_config,
    device_map="auto",
)
```

Then LoRA adapters are added on top of this quantized base.

## LoRA vs QLoRA

### LoRA

- frozen base model
- adapter training
- base model may still require substantial memory

### QLoRA

- quantized frozen base model
- adapter training
- much more memory-efficient

Strong answer:

> LoRA reduces trainable parameters, while QLoRA goes further by also quantizing the frozen base model so that larger models become fine-tunable on modest hardware.

## When LoRA is a Great Choice

- large LLMs
- limited GPU budget
- multiple domain-specific adapters
- need to swap domain behaviors cheaply

## When Full Fine-Tuning May Still Win

- extremely large or complex domain shift
- maximum quality matters more than cost
- enough compute and operational support exist

## Target Module Choice

A subtle but important topic.

Why module choice matters:

- some modules affect reasoning and generation more
- some target sets are cheaper
- wrong target set can reduce quality

Practical approach:

1. start with known target modules for the model family
2. benchmark
3. expand only if needed

## Common LoRA Failure Modes

### 1. Rank too low

Symptoms:

- weak task adaptation

### 2. Rank too high

Symptoms:

- more memory
- overfitting risk
- diminishing returns

### 3. Wrong target modules

Symptoms:

- unstable or weak gains

### 4. Blaming LoRA for bad data

Symptoms:

- poor results no matter what hyperparameters you try

Cause:

- dataset problem, not tuning method

## Adapter Merging

LoRA adapters can often be:

- kept separate and loaded dynamically
- merged into the base model for serving

This is a practical deployment decision.

Keeping adapters separate helps when:

- many domains / customers exist
- frequent swapping is needed

Merging may help when:

- you want simpler inference deployment

## Strong Interview Answer

> LoRA is a parameter-efficient fine-tuning technique that freezes the original model and learns a low-rank update to selected layers. It is popular because it achieves strong adaptation quality with far lower memory and compute than full fine-tuning. QLoRA adds quantization of the frozen base model, which makes fine-tuning even larger models feasible on smaller hardware.

## Summary

For interviews, remember this:

- LoRA = small learned weight update
- QLoRA = LoRA + quantized base model
- both are about practical adaptation under compute constraints
