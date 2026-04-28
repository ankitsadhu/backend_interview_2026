# LLM Inference and Generation Learning Path

This track covers the lower-level mechanics behind modern LLM applications: how models are made smaller, how generation is made faster, how outputs are constrained, and how multimodal systems are built.

It is designed for MANG-level interview preparation from beginner to advanced, with emphasis on:

- first-principles mental models
- coding examples
- serving and production tradeoffs
- cross-question traps
- system design reasoning

## Contents

1. [Quantization](01_quantization.md) - precision, memory math, PTQ, QAT, GPTQ, AWQ, GGUF, QLoRA connection
2. [KV Cache and Context Optimization](02_kv_cache_and_context_optimization.md) - attention cost, prefill vs decode, paged attention, long context
3. [Structured Outputs](03_structured_outputs.md) - JSON mode, schemas, constrained decoding, validation and repair loops
4. [Multimodal Systems](04_multimodal_systems.md) - vision-language architecture, embeddings, OCR, audio, production design
5. [Serving, Latency, and Production Patterns](05_serving_latency_and_production_patterns.md) - batching, streaming, speculative decoding, routing, observability
6. [Interview Questions](06_interview_questions.md) - MANG-style questions, cross questions, concise answers

## Mental Model

```text
User Request
  |
  v
Input processing
  |       \
  |        +--> text tokens
  |        +--> image / audio / document encoders
  v
Model inference
  |
  +--> prefill prompt tokens
  +--> decode new tokens using KV cache
  +--> optional constrained decoding
  |
  v
Post-processing
  |
  +--> validate structured output
  +--> stream / return answer
  +--> log latency, cost, quality signals
```

## Why This Matters in Interviews

Many candidates can call an LLM API.

Fewer can explain:

- why long prompts are expensive
- how KV cache improves decoding
- why quantization reduces memory but may affect quality
- why JSON prompting is weaker than constrained decoding
- how a vision-language model actually connects images to text
- how to design a low-latency production LLM service

This track is for those cross questions.

