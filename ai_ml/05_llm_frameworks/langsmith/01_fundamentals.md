# LangSmith Fundamentals

## What is LangSmith?

LangSmith is a developer platform for **observability, evaluation, testing, and debugging** of LLM applications.

If LangChain helps you build LLM workflows, LangSmith helps you answer:

- What exactly happened during a bad response?
- Which prompt version performed better?
- Why did the agent call the wrong tool?
- Where did latency or cost increase?
- How do we compare experiments before deployment?

## Why We Need It

Traditional backend debugging uses logs, metrics, and traces.

LLM systems add new failure types:

- non-deterministic outputs
- prompt regressions
- retrieval quality issues
- tool selection mistakes
- hallucinations
- token explosion
- hidden latency from chained model calls

Plain application logs are usually not enough because they miss:

- prompt templates
- model parameters
- intermediate tool calls
- retrieved documents
- structured feedback on answer quality

## Core Concepts

### 1. Run

A **run** is a tracked execution unit.

Examples:

- one model call
- one retriever call
- one chain execution
- one tool invocation
- one complete agent request

### 2. Trace

A **trace** is the full tree of nested runs for a request.

```text
User asks: "Summarize Q4 revenue risk"
|
+-- Root run: finance-assistant
    |
    +-- Retriever run: vector search
    +-- Tool run: SQL query
    +-- LLM run: reasoning + answer generation
    +-- Parser run: structured JSON output
```

### 3. Dataset

A dataset is a curated set of examples used for:

- prompt evaluation
- regression testing
- benchmarking model changes

Example dataset rows:

- customer support query -> expected answer traits
- document question -> ground truth answer
- tool-use request -> expected tool call sequence

### 4. Evaluation

Evaluation measures quality.

This can be:

- exact match
- semantic similarity
- correctness judged by another LLM
- human feedback
- custom business rule checks

### 5. Feedback

Feedback is human or automated annotation on a run.

Examples:

- thumbs up / thumbs down
- factuality score
- hallucination flag
- "used wrong tool"
- "tone too verbose"

## LangSmith in the LLM Stack

```text
Application Layer
  FastAPI / Django / Worker / Agent service

Orchestration Layer
  LangChain / LangGraph / custom pipelines

Model + Retrieval Layer
  OpenAI / Anthropic / Gemini / vector DB / tools

Observability + Evaluation Layer
  LangSmith
```

## Where It Fits in Production

LangSmith is not your primary app database or queue.

It complements:

- application logs
- APM tools
- metrics systems
- feature flag systems
- CI pipelines

A mature LLM system often uses:

- Prometheus / Datadog for infra metrics
- Sentry for app exceptions
- LangSmith for LLM workflow traces and evals

## Minimal Setup

### Environment variables

```bash
export LANGSMITH_API_KEY="your-api-key"
export LANGSMITH_TRACING="true"
export LANGSMITH_PROJECT="mang-interview-prep"
```

### Python example with OpenAI wrapper

```python
from langsmith import traceable
from openai import OpenAI

client = OpenAI()

@traceable(name="simple_qa")
def answer_question(question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return response.choices[0].message.content

print(answer_question("What is LangSmith used for?"))
```

This gives you a visible run with:

- input question
- model used
- response
- timing
- nested trace context if more calls are added

## With LangChain

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "mang-interview-prep"

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert interview coach."),
    ("human", "Explain {topic} in 5 bullet points."),
])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = prompt | llm

result = chain.invoke({"topic": "LangSmith"})
print(result.content)
```

LangSmith automatically captures prompt, inputs, outputs, timing, and nested steps.

## Interview-Worthy Benefits

### Debugging

If a user says, "The answer was wrong," LangSmith helps inspect:

- the exact prompt
- retrieved chunks
- tool arguments
- intermediate outputs
- final answer

### Regression Detection

If you changed:

- prompt wording
- model version
- retriever settings
- chunk size

you can compare before vs after on the same dataset.

### Faster Incident Response

Instead of reading raw logs, an engineer can inspect one trace and identify:

- model timeout
- empty retrieval result
- parser failure
- bad tool selection
- runaway token usage

## Common Misconceptions

### "LangSmith is only for LangChain"

No. It works best with the LangChain ecosystem, but you can instrument custom code too.

### "Tracing alone is enough"

No. Tracing tells you what happened. Evaluation tells you whether it was good.

### "If the app works in demo, we do not need LangSmith"

Demo success is not production reliability. LLM systems fail in subtle ways under real traffic.

## Real-World Problems It Helps Solve

### Problem: bad answers after prompt update

Use dataset evals to compare old vs new prompts.

### Problem: agent became slower

Inspect traces to see:

- extra model calls
- retries
- slow retrievers
- tool latency

### Problem: hallucinations increased

Check whether retrieval returned poor context or whether prompt grounding weakened.

### Problem: costs suddenly doubled

Trace token usage by workflow, prompt version, customer segment, or endpoint.

## What a Strong Interview Answer Sounds Like

If asked "Why LangSmith?" a strong answer is:

> LangSmith provides observability and evaluation for LLM applications. In traditional systems, logs and APM help us debug deterministic code paths. In LLM systems we also need visibility into prompts, model calls, retrieval results, tool usage, and output quality. LangSmith helps us trace complete workflows, compare prompt or model variants, attach feedback, and run regression evaluations before pushing changes to production.

## Summary

LangSmith is most useful when you move from:

- toy demo -> real application
- single prompt -> multi-step workflow
- manual spot-checking -> repeatable evaluation
- "it seems okay" -> measurable quality and reliability
