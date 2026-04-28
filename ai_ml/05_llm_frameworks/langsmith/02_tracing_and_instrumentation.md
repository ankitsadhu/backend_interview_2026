# Tracing and Instrumentation

## Why Tracing Matters for LLM Apps

An LLM request is rarely one API call in production.

It may include:

- prompt construction
- retrieval
- ranking
- multiple model calls
- tool execution
- output parsing
- retries and fallbacks

Without tracing, all of this becomes a black box.

## Mental Model

```text
HTTP request
  -> root run
     -> retriever run
     -> reranker run
     -> tool run
     -> LLM run
     -> parser run
```

Each child run adds visibility into one step.

## What to Capture

At minimum, capture:

- user input
- system prompt / template version
- model name
- temperature and decoding params
- retrieved documents or IDs
- tool name and arguments
- latency
- token usage
- output
- error state

Useful metadata:

- customer_id
- tenant_id
- session_id
- endpoint
- release version
- prompt version
- experiment tag

## Basic Instrumentation with `@traceable`

```python
import time
from langsmith import traceable
from openai import OpenAI

client = OpenAI()

@traceable(name="retrieve_context", run_type="retriever")
def retrieve_context(query: str) -> list[str]:
    # Pretend this comes from a vector DB
    docs = [
        "LangSmith supports tracing and evaluation.",
        "LangSmith helps debug LLM apps in production.",
    ]
    return docs

@traceable(name="generate_answer", run_type="llm")
def generate_answer(question: str, context: list[str]) -> str:
    joined_context = "\n".join(context)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "Answer only from the provided context."},
            {
                "role": "user",
                "content": f"Question: {question}\n\nContext:\n{joined_context}",
            },
        ],
    )
    return response.choices[0].message.content

@traceable(name="rag_pipeline")
def rag_pipeline(question: str) -> str:
    start = time.time()
    docs = retrieve_context(question)
    answer = generate_answer(question, docs)
    print(f"pipeline took {time.time() - start:.2f}s")
    return answer
```

This creates a nested trace instead of one giant unstructured log.

## Tagging and Metadata

Good teams make traces searchable.

```python
from langsmith import traceable

@traceable(
    name="customer_support_agent",
    metadata={
        "service": "support-api",
        "env": "prod",
        "feature": "refund-assistant",
        "prompt_version": "v12",
    },
    tags=["refunds", "priority-high"],
)
def run_support_agent(question: str) -> str:
    return f"Processed: {question}"
```

This helps answer:

- Which traces belong to one release?
- Which prompt version caused regressions?
- Which tenant is generating most errors?

## Capturing Tool Calls

Interviewers often ask how to debug agents calling tools incorrectly.

```python
from langsmith import traceable

@traceable(name="fetch_order", run_type="tool")
def fetch_order(order_id: str) -> dict:
    return {"order_id": order_id, "status": "shipped", "eta_days": 2}

@traceable(name="support_agent")
def support_agent(order_id: str) -> str:
    order = fetch_order(order_id)
    return f"Order {order['order_id']} is {order['status']} and arrives in {order['eta_days']} days."
```

If the agent passes the wrong `order_id`, trace inspection makes that obvious.

## Instrumenting LangChain Pipelines

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "langsmith-interview"

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a production debugging assistant."),
    ("human", "Analyze the issue: {incident}"),
])

chain = prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0)

response = chain.invoke({
    "incident": "A retrieval pipeline returns outdated policy documents."
})

print(response.content)
```

Automatic tracing is helpful, but you still need good metadata and naming.

## Naming Conventions

Poor run names:

- `step1`
- `llm_call`
- `process`

Good run names:

- `retrieve_policy_documents`
- `classify_ticket_intent`
- `generate_refund_response`
- `parse_structured_plan`

Good names reduce incident triage time.

## Production Problem: Missing Context in Traces

Bad trace:

- only final answer captured
- no prompt
- no retrieved docs
- no model config

Consequence:

- can reproduce nothing
- cannot compare versions
- no clue whether bug came from retrieval or generation

Fix:

- trace every meaningful step
- add prompt version metadata
- attach document IDs and retrieval scores

## Production Problem: Over-Instrumentation

Some teams trace everything at full payload detail and hit:

- privacy concerns
- noisy dashboards
- high storage cost
- hard-to-read traces

Best practice:

- capture enough for debugging
- redact secrets and PII
- truncate huge payloads
- sample low-value traffic when appropriate

## What to Log vs What to Trace

Use logs for:

- service startup
- infra events
- business events
- exceptions outside LLM workflow

Use LangSmith traces for:

- prompts
- model responses
- tool decisions
- retrieval behavior
- evaluation outcomes

## Real-World Debugging Workflow

Suppose a user says: "Your finance bot gave the wrong revenue number."

Use the trace to inspect:

1. user query
2. retrieved documents
3. whether the correct table/tool was called
4. prompt grounding instructions
5. final model output

Typical root causes:

- stale retrieval index
- wrong SQL tool arguments
- prompt did not force citation
- model answered from prior knowledge
- parser dropped a field

## MANG-Level Interview Insight

Tracing is not just for debugging single failures. It supports:

- release comparison
- cost attribution
- latency decomposition
- prompt governance
- postmortems

That is the difference between a demo and an operable platform.

## Summary

Tracing gives you the execution tree.

A good trace should let another engineer answer:

- what happened
- in what order
- with which inputs
- under which configuration
- why the output failed or succeeded
