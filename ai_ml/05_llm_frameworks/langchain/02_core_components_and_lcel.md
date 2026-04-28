# Core Components and LCEL

## The Core Building Blocks

LangChain is easiest to understand when broken into pieces.

## 1. Prompt Templates

Prompt templates help you parameterize prompts cleanly.

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant for backend interviews."),
    ("human", "Explain {topic} with one example."),
])

messages = prompt.invoke({"topic": "caching"})
print(messages)
```

Benefits:

- reuse
- consistency
- easier versioning

## 2. Chat Models

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)
```

LangChain standardizes model invocation so you can swap providers more easily.

## 3. Output Parsers

Raw text is often not enough in backend systems.

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
```

For structured outputs, parsers are even more useful.

```python
from pydantic import BaseModel, Field

class TicketClassification(BaseModel):
    priority: str = Field(description="low, medium, high")
    team: str = Field(description="team responsible")
```

## 4. Runnables

Runnables are the core composable unit in modern LangChain.

Examples:

- prompt template
- model
- parser
- retriever
- lambda transform

These can be chained together.

## LCEL: LangChain Expression Language

LCEL is the composition syntax used to wire components together.

The pipe operator makes pipelines readable.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Explain {topic} for a senior backend interview."
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

chain = prompt | llm | parser

result = chain.invoke({"topic": "LangChain LCEL"})
print(result)
```

## Why LCEL Matters

Before LCEL, orchestration code often became hard to read.

LCEL improves:

- readability
- composability
- standardization
- step reuse

## Using `RunnableLambda`

Useful when you want custom Python logic inside a pipeline.

```python
from langchain_core.runnables import RunnableLambda

def clean_text(text: str) -> str:
    return text.strip().lower()

normalizer = RunnableLambda(clean_text)

pipeline = normalizer
print(pipeline.invoke("  Hello World  "))
```

## Parallel Composition

Sometimes you want multiple derived fields at once.

```python
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel({
    "original": RunnableLambda(lambda x: x),
    "length": RunnableLambda(lambda x: len(x)),
})

print(parallel.invoke("langchain"))
```

This becomes useful for:

- feature extraction
- parallel preprocessing
- branching data preparation

## Prompt + Model + Parser is the Basic Pattern

The most common LangChain shape is:

```text
input -> prompt -> model -> parser
```

This is the backbone of many production flows.

## Structured Output Example

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class IncidentSummary(BaseModel):
    severity: str = Field(description="low, medium, high")
    root_cause: str
    action_items: list[str]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = llm.with_structured_output(IncidentSummary)

result = structured_llm.invoke(
    "Database latency spiked because connection pool limits were exhausted."
)

print(result)
```

This is very interview-relevant because real systems often need structured responses, not essays.

## Common LCEL Use Cases

### Routing

Use a first step to classify request type, then send it to a downstream chain.

### Enrichment

Add retrieval results or metadata before prompting.

### Validation

Run parser and schema checks after generation.

### Transformation

Normalize documents or inputs between stages.

## Real-World Problems

### Problem: prompt logic repeated in 8 services

Fix:

- centralize prompt templates
- reuse LCEL chains

### Problem: outputs are hard to consume downstream

Fix:

- use structured outputs instead of free-form prose

### Problem: every engineer builds their own ad hoc LLM wrapper

Fix:

- standardize model and parser composition through runnables

## Failure Modes

### 1. Too much abstraction

If the chain is tiny, LCEL may feel heavier than plain Python.

### 2. Hidden transformations

If custom runnables are poorly named, debugging becomes hard.

### 3. Fragile structured parsing

Even good models can return malformed data, so parsers need fallback handling.

## Good Interview Answer

> LCEL is LangChain's composition model for building pipelines out of reusable runnables like prompts, models, parsers, and custom transforms. It makes LLM workflows more declarative and composable, which is useful when multiple steps need to be reused or inspected. I would especially use it for prompt-model-parser pipelines, routing, and structured output workflows.

## Summary

To get strong at LangChain, understand this deeply:

- prompt templates define intent
- models generate or reason
- parsers enforce structure
- runnables compose steps
- LCEL is the glue
