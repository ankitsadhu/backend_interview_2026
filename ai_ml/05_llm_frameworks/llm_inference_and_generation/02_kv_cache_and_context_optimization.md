# KV Cache and Context Optimization

## Why Attention Becomes Expensive

In a transformer, each token attends to previous tokens.

For a sequence length `T`, attention compares tokens with other tokens. This creates a cost that grows heavily with context length.

During generation, the model produces one token at a time:

```text
prompt tokens -> next token -> next token -> next token
```

Without caching, the model would repeatedly recompute attention keys and values for all previous tokens.

## Query, Key, Value Mental Model

For each token, attention creates:

- query: what this token is looking for
- key: what this token offers for matching
- value: information to pass forward

For a new generated token, old keys and values do not change. So we cache them.

## What KV Cache Stores

KV cache stores the key and value tensors for previous tokens in each transformer layer.

```text
Layer 1: K,V for tokens 1..T
Layer 2: K,V for tokens 1..T
...
Layer N: K,V for tokens 1..T
```

When generating token `T + 1`, the model only computes Q/K/V for the new token and reuses old K/V.

## Prefill vs Decode

LLM serving has two major phases.

### Prefill

The model processes the input prompt.

Characteristics:

- many tokens processed in parallel
- compute-heavy
- builds the initial KV cache

### Decode

The model generates output tokens one by one.

Characteristics:

- sequential
- latency-sensitive
- uses KV cache heavily

Strong interview answer:

```text
Prefill handles the prompt in parallel and creates KV cache. Decode generates one token at a time and reuses the cache, so it is often memory-bandwidth and scheduling sensitive.
```

## KV Cache Memory Formula

Approximate KV cache memory:

```text
layers * tokens * hidden_size * 2(K and V) * bytes
```

More exact formulas depend on number of KV heads, grouped-query attention, and implementation.

The key point:

```text
KV cache grows linearly with context length and batch size.
```

That is why long-context serving can become memory-bound even when weights are quantized.

## Simple KV Cache Estimator

```python
def estimate_kv_cache_gb(
    layers: int,
    tokens: int,
    hidden_size: int,
    bytes_per_value: int = 2,
    batch_size: int = 1,
) -> float:
    total_bytes = batch_size * layers * tokens * hidden_size * 2 * bytes_per_value
    return total_bytes / (1024 ** 3)


print(round(estimate_kv_cache_gb(
    layers=32,
    tokens=8192,
    hidden_size=4096,
    bytes_per_value=2,
    batch_size=4,
), 2))
```

This rough estimator helps explain why a quantized model can still run out of memory at long context.

## Context Optimization Techniques

### Prompt Compression

Reduce irrelevant prompt tokens before inference.

Examples:

- summarize older conversation
- remove duplicate retrieved chunks
- trim boilerplate
- keep only task-relevant fields

### Retrieval Instead of Huge Context

Instead of sending every document, retrieve the top relevant evidence.

Good answer:

```text
Long context is not a replacement for retrieval quality. It increases capacity, but noise still hurts reasoning and cost.
```

### Sliding Window Attention

The model attends only to a recent window of tokens.

Useful for:

- long streams
- chat history
- local coherence

Limitation:

- information outside the window may be lost

### Chunked Attention

Process long inputs in chunks to reduce memory pressure.

Useful for:

- long documents
- summarization
- document QA

### PagedAttention

PagedAttention, popularized by vLLM, manages KV cache like virtual memory pages.

The core idea:

```text
Do not require each request's KV cache to live in one contiguous memory block.
```

This improves memory utilization and helps serve many concurrent requests.

## Batching and KV Cache

Batching improves throughput, but different requests have different prompt lengths and output lengths.

Problems:

- padding waste
- memory fragmentation
- long requests blocking short requests
- unpredictable decode lengths

Production servers use scheduling strategies such as continuous batching to add and remove requests dynamically.

## Long-Context Failure Modes

Long context does not mean perfect memory.

Common problems:

- model ignores middle content
- irrelevant context distracts the model
- latency increases
- cost increases
- KV cache memory grows
- citations become harder to verify

## Coding Example: Context Budgeting

```python
def build_context(chunks, max_tokens, count_tokens):
    selected = []
    used = 0

    for chunk in chunks:
        cost = count_tokens(chunk["text"])
        if used + cost > max_tokens:
            continue
        selected.append(chunk)
        used += cost

    return selected
```

This is intentionally simple. In production, rank, deduplicate, filter by permissions, and preserve source metadata.

## Cross Questions

### If KV cache speeds decoding, why not cache everything forever?

Because KV cache consumes memory proportional to sequence length, layers, hidden size, and batch size. Keeping everything forever reduces concurrency and can cause out-of-memory failures.

### Does quantizing weights reduce KV cache memory?

Not necessarily. Weight quantization reduces model weight memory. KV cache may still be FP16/BF16 unless the runtime supports KV cache quantization.

### Why can a short output with a huge prompt be slow?

Because the prefill phase must process the full prompt before decoding begins.

### Why can a short prompt with a long output be slow?

Because decode is sequential and each output token depends on previous output tokens.

