# Serving, Latency, and Production Patterns

## Main Latency Components

LLM request latency usually includes:

- network overhead
- queueing
- tokenization
- prefill
- decoding
- post-processing
- validation
- tool calls or retrieval

For interviews, separate:

```text
time to first token
```

from:

```text
time to full response
```

Streaming improves perceived latency, but it does not necessarily reduce total compute.

## Throughput vs Latency

Throughput is how much work the system completes per second.

Latency is how long one request waits.

Batching can improve throughput but hurt latency if requests wait too long in a queue.

Production systems balance:

- batch size
- queue timeout
- request priority
- max output tokens
- model size
- hardware utilization

## Continuous Batching

Static batching waits for a group of requests and runs them together.

Continuous batching dynamically adds new requests as old requests finish.

This matters because LLM requests have variable output lengths.

Strong answer:

```text
Continuous batching improves GPU utilization for autoregressive decoding because requests can enter and leave the batch at different decode steps.
```

## Speculative Decoding

Speculative decoding uses a smaller draft model to propose tokens, then a larger target model verifies them.

If the draft is good, multiple tokens are accepted at once.

Useful when:

- target model is large
- draft model is much cheaper
- output distribution is predictable enough

Tradeoffs:

- more implementation complexity
- draft model memory
- benefit depends on acceptance rate

## Model Routing

Not every request needs the largest model.

Routing patterns:

- simple requests -> small model
- complex requests -> larger model
- risky requests -> safer or more constrained path
- low-priority batch jobs -> cheaper model

Interview caveat:

```text
Routing needs evaluation. A bad router can silently reduce quality.
```

## Caching

Useful cache types:

- exact prompt cache
- semantic cache
- embedding cache
- retrieval result cache
- tool result cache
- KV prefix cache

Cache carefully when responses depend on user permissions, freshness, or private data.

## Guardrails and Limits

Set explicit limits:

- max input tokens
- max output tokens
- request timeout
- tool-call depth
- retry count
- concurrent requests per tenant
- file size for multimodal inputs

Limits are part of reliability, not just cost control.

## Minimal FastAPI Serving Shape

```python
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 256


class GenerateResponse(BaseModel):
    text: str
    input_tokens: int
    output_tokens: int


@app.post("/generate")
def generate(req: GenerateRequest) -> GenerateResponse:
    if req.max_tokens > 1024:
        raise ValueError("max_tokens too large")

    # Replace this with your model runtime call.
    text = "model response"

    return GenerateResponse(
        text=text,
        input_tokens=len(req.prompt.split()),
        output_tokens=len(text.split()),
    )
```

Production version needs authentication, rate limits, proper token counting, tracing, structured errors, and safe model runtime integration.

## Observability

Track:

- prompt tokens
- output tokens
- time to first token
- total latency
- queue time
- model name and version
- retry count
- validation failure rate
- tool-call count
- user-visible errors
- cost per request

For RAG and multimodal systems, also track retrieval and extraction metrics.

## Incident Examples

### Token Explosion

A prompt template accidentally includes full chat history and all retrieved documents.

Fix:

- context budget
- truncation policy
- prompt tests
- token dashboards

### Structured Output Retry Storm

Model starts producing invalid tool arguments. Repair loop retries every request three times.

Fix:

- cap retries
- alert on validation failures
- fallback model or fallback flow
- regression eval

### Long-Context Memory Failure

New enterprise customer uploads huge documents. KV cache usage spikes.

Fix:

- file limits
- retrieval-first design
- chunking
- request queue controls
- long-context model only for selected tasks

## Cross Questions

### Does streaming reduce model compute?

No. It improves perceived responsiveness by sending tokens early.

### What is the first thing you check when latency increases?

Break latency into queue time, prefill time, decode time, retrieval/tool time, and post-processing. The fix depends on which component changed.

### How do you reduce cost without hurting quality too much?

Use smaller models for simple tasks, limit context, cache safe repeat work, improve retrieval precision, cap output length, and evaluate quality on real tasks.

### Why is max output token control important?

Autoregressive decoding is sequential. Long outputs increase latency, cost, and GPU occupancy.

