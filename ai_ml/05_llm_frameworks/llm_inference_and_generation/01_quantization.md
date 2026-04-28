# Quantization

## Core Idea

Neural networks store weights as numbers.

Quantization stores those numbers in lower precision.

Instead of using 32-bit floating point for every weight, we may use:

- FP16 / BF16
- INT8
- INT4
- NF4

The main goal is to reduce memory, bandwidth, and sometimes latency.

## First-Principles Memory Math

If a model has `N` parameters:

```text
memory = N * bytes_per_parameter
```

For a 7B parameter model:

```text
FP32: 7B * 4 bytes  = 28 GB
FP16: 7B * 2 bytes  = 14 GB
INT8: 7B * 1 byte   = 7 GB
INT4: 7B * 0.5 byte = 3.5 GB
```

This is only weight memory. Real inference also needs KV cache, activations, runtime overhead, tokenizer buffers, and framework overhead.

## Why Lower Precision Can Work

Model weights do not need infinite precision. Many values can be approximated without changing model behavior too much.

Quantization maps a high-precision range into a smaller set of representable values.

Example:

```text
float values: [-1.00, -0.23, 0.01, 0.77, 1.15]
int8 buckets: [-127 ... 127]
```

The model uses approximate values during inference.

## Scale and Zero Point

A common affine quantization formula is:

```text
real_value ≈ scale * (quantized_value - zero_point)
```

Where:

- `scale` maps integer steps back to real-number distance
- `zero_point` represents real zero in quantized space

For symmetric quantization, zero point is often `0`.

## Per-Tensor vs Per-Channel Quantization

### Per-tensor

One scale is used for a whole tensor.

Pros:

- simple
- fast

Cons:

- one outlier can hurt precision for the whole tensor

### Per-channel

Different channels get different scales.

Pros:

- better quality
- handles uneven value distributions

Cons:

- more metadata
- slightly more complexity

## PTQ vs QAT

### Post-Training Quantization

PTQ quantizes an already trained model.

Use when:

- you want fast deployment
- training data is limited
- small quality loss is acceptable

### Quantization-Aware Training

QAT simulates quantization during training.

Use when:

- quality is very sensitive
- you can afford training
- model must run at low precision in production

Strong interview answer:

```text
PTQ is cheaper and easier, while QAT usually preserves quality better because the model learns under quantization noise.
```

## GPTQ, AWQ, and GGUF

### GPTQ

GPTQ is a post-training method that quantizes weights while trying to minimize reconstruction error layer by layer.

Useful for:

- local inference
- low-bit LLM deployment

### AWQ

AWQ focuses on activation-aware quantization. It tries to protect important weights based on activation patterns.

Useful idea:

```text
Not all weights are equally important for output quality.
```

### GGUF

GGUF is a file format commonly used by `llama.cpp`-style local inference runtimes.

It matters because deployment is not only an algorithm problem. The runtime and model format decide what can run efficiently on a target machine.

## Quantization vs Pruning vs Distillation

### Quantization

Same architecture, lower-precision numbers.

### Pruning

Remove weights, heads, neurons, or layers.

### Distillation

Train a smaller model to imitate a larger model.

Interview trap:

```text
Quantization compresses numeric representation. It does not necessarily reduce parameter count.
```

## Quantization and Fine-Tuning

QLoRA combines:

- quantized frozen base model
- trainable LoRA adapters

The base model is compressed to reduce memory. The adapters remain trainable.

This is why QLoRA is popular for fine-tuning large models on limited hardware.

## Simple Python Memory Estimator

```python
def estimate_weight_memory(params: int, bits_per_weight: int) -> float:
    bytes_per_weight = bits_per_weight / 8
    gb = params * bytes_per_weight / (1024 ** 3)
    return gb


for bits in [32, 16, 8, 4]:
    print(bits, round(estimate_weight_memory(7_000_000_000, bits), 2), "GB")
```

Expected output is approximately:

```text
32 26.08 GB
16 13.04 GB
8 6.52 GB
4 3.26 GB
```

The number differs from decimal GB estimates because computers often report GiB.

## Production Tradeoffs

Quantization helps with:

- memory footprint
- ability to run larger models
- deployment on smaller GPUs or CPUs
- lower bandwidth pressure

Quantization may hurt:

- factual accuracy
- reasoning quality
- tool-call argument precision
- multilingual quality
- rare-token behavior

Always evaluate on your real task. Generic benchmark wins do not guarantee product quality.

## Cross Questions

### Does INT4 always make inference 4x faster than FP16?

No. It may reduce memory bandwidth, but speed depends on kernels, hardware support, batch size, model architecture, and dequantization overhead.

### Why can quantization hurt structured outputs?

If quantization changes token probabilities near decision boundaries, the model may produce malformed JSON, wrong enum values, or unstable tool arguments.

### Would you quantize embeddings?

Sometimes, but carefully. Vector similarity is sensitive to geometry. Quantized embeddings can save memory, but retrieval quality must be evaluated.

### What would you test before shipping a quantized model?

- task accuracy
- hallucination rate
- structured output validity
- latency
- throughput
- memory
- worst-case prompts
- language and domain slices

