# Interview Questions

## 1. What is quantization?

Quantization stores model weights or activations in lower precision, such as INT8 or INT4, to reduce memory and sometimes improve inference efficiency.

## 2. Does quantization reduce the number of parameters?

No. It usually keeps the same number of parameters but stores each parameter with fewer bits.

## 3. Why can quantization hurt model quality?

Lower precision introduces approximation error. If important weights or activations are distorted, token probabilities can shift and quality can drop.

## 4. What is the difference between PTQ and QAT?

PTQ quantizes a model after training. QAT simulates quantization during training so the model can adapt to quantization noise.

## 5. What is QLoRA?

QLoRA fine-tunes small LoRA adapters on top of a quantized frozen base model. It reduces memory while keeping the trainable part small.

## 6. What is KV cache?

KV cache stores attention keys and values from previous tokens so the model does not recompute them during autoregressive decoding.

## 7. Why does KV cache matter?

It makes generation much faster, especially during decode, but it consumes memory that grows with context length and batch size.

## 8. What is prefill vs decode?

Prefill processes the input prompt and builds the KV cache. Decode generates new tokens one at a time using that cache.

## 9. Why can long context be expensive even with a quantized model?

Quantization reduces weight memory, but long context increases prefill work and KV cache memory.

## 10. What is PagedAttention?

PagedAttention manages KV cache in pages instead of requiring contiguous memory, improving memory utilization for serving many concurrent requests.

## 11. What are structured outputs?

Structured outputs are model responses constrained or validated into predictable formats such as JSON objects, tool calls, or schema-compliant records.

## 12. Is asking the model to output JSON enough?

No. Prompting can still produce invalid or schema-wrong output. Production systems use validation and sometimes constrained decoding.

## 13. What is constrained decoding?

Constrained decoding restricts the allowed next tokens so generated output follows a grammar, JSON schema, enum, or other formal structure.

## 14. What is function calling?

Function calling is structured generation where the model emits a tool name and typed arguments. The application validates and executes the tool.

## 15. Should the app execute every tool call the model emits?

No. Tool calls must be validated, authorized, logged, and sometimes approved by a human, especially if they cause side effects.

## 16. What is a multimodal model?

A multimodal model processes multiple data types, such as text and images, or text and audio.

## 17. How does a vision-language model connect images to text?

A vision encoder converts image patches into embeddings, and a projection layer maps them into a representation the language model can consume.

## 18. When is OCR better than a vision-language model?

OCR is better when exact text extraction from documents is the main requirement. A vision-language model is better when layout, diagrams, or visual relationships matter.

## 19. What is multimodal RAG?

Multimodal RAG retrieves and grounds answers using evidence from multiple modalities, such as text chunks, page images, charts, and transcripts.

## 20. What is continuous batching?

Continuous batching lets LLM serving systems dynamically add and remove requests during decoding, improving GPU utilization despite variable output lengths.

## 21. What is speculative decoding?

Speculative decoding uses a small draft model to propose tokens and a larger model to verify them, potentially reducing latency.

## 22. Does streaming reduce total compute?

No. It improves perceived latency by returning tokens earlier, but the model still performs the generation work.

## 23. How would you debug high LLM latency?

I would break latency into queueing, tokenization, prefill, decode, retrieval or tool calls, validation, and network time. Then I would optimize the component causing the regression.

## 24. How would you reduce LLM serving cost?

I would reduce unnecessary context, cache safe repeat work, route simple requests to smaller models, cap output tokens, batch where possible, and evaluate quality after each change.

## 25. What metrics would you monitor for an LLM service?

Prompt tokens, output tokens, time to first token, total latency, queue time, validation failure rate, retry count, error rate, cost, model version, and quality metrics.

## Cross-Question Drills

### If a quantized model is faster, why not always quantize?

Because quality can drop, hardware kernels may not speed up, some tasks are precision-sensitive, and the deployment runtime may add dequantization overhead.

### If long-context models exist, why use RAG?

Long context gives capacity, but RAG improves relevance, freshness, access control, citations, and cost. Long context can still be noisy and expensive.

### If JSON mode guarantees valid JSON, why validate?

Because valid JSON can still violate the schema, business rules, permissions, or safety requirements.

### If a multimodal model can read images, why run OCR?

OCR gives exact searchable text, lower-cost indexing, and better auditability. Vision models help when visual layout or non-text content matters.

### If streaming improves UX, what can go wrong?

You may stream content before validation, leak partial unsafe output, or make structured parsing harder. Some workflows should validate before display.

## System Design Prompt

Design an enterprise document assistant that supports PDFs, screenshots, and text documents.

Strong answer should include:

- ingestion pipeline for text, OCR, image assets, and metadata
- access control before retrieval
- text and image embeddings
- retrieval with reranking
- selective VLM calls for pages requiring visual reasoning
- structured citations
- latency budgets and async processing
- evaluation for OCR, retrieval, answer quality, and hallucination
- observability for tokens, cost, failures, and user feedback

## Final Interview Tip

For MANG-level answers, connect mechanism to tradeoff:

```text
Quantization saves memory but may affect quality.
KV cache speeds decode but consumes memory.
Structured outputs improve reliability but still need validation.
Multimodal models add capability but increase latency, cost, and evaluation complexity.
```

