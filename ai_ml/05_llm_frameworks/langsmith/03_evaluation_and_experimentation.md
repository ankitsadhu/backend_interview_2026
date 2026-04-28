# Evaluation and Experimentation

## Why Evaluation is Hard in LLM Systems

Traditional software can often be tested with exact expected outputs.

LLM systems are different:

- multiple answers may be acceptable
- output quality can be subjective
- correctness may depend on context
- model behavior changes with prompt, model, and retrieval changes

That is why strong teams move from ad hoc testing to structured evaluation.

## Types of Evaluation

### 1. Offline Evaluation

Run the system on a fixed dataset before release.

Used for:

- prompt comparisons
- model migration
- retriever tuning
- parser validation

### 2. Online Evaluation

Measure quality in production using:

- human ratings
- click-through
- resolution rate
- escalation rate
- citation usage

### 3. Human Evaluation

Still necessary for:

- tone
- helpfulness
- subtle factual quality
- domain-specific correctness

### 4. LLM-as-Judge

Another model scores the output against a rubric.

Useful but should be used carefully because judges can be biased or inconsistent.

## Evaluation Dimensions

Common dimensions:

- correctness
- groundedness
- relevance
- completeness
- safety
- latency
- cost
- format compliance

For RAG systems add:

- retrieval precision
- retrieval recall
- answer citation quality
- faithfulness to sources

## Dataset Design

A good dataset should contain:

- representative production queries
- edge cases
- failure examples from past incidents
- ambiguous queries
- adversarial queries
- long-context queries

Example rows:

| Input | Expected check |
|------|----------------|
| "What is our EU data retention policy?" | Must use policy docs, not general model knowledge |
| "Refund customer for order 123?" | Must call internal order tool before answering |
| "Summarize this 20-page contract" | Must handle long context without truncation failure |

## Simple Evaluation Example

```python
from langsmith import Client

client = Client()

dataset_name = "support-agent-regression-suite"

# Pseudocode style example
examples = [
    {
        "inputs": {"question": "What is LangSmith?"},
        "outputs": {"must_mention": "observability"},
    },
    {
        "inputs": {"question": "Why do we need evaluations?"},
        "outputs": {"must_mention": "regression"},
    },
]

for row in examples:
    print("Would add to dataset:", row)
```

In practice you want datasets to come from:

- real tickets
- search queries
- support transcripts
- annotated production failures

## Custom Evaluator Example

```python
def keyword_evaluator(run_output: str, expected_keyword: str) -> dict:
    passed = expected_keyword.lower() in run_output.lower()
    return {
        "score": 1.0 if passed else 0.0,
        "comment": f"Expected keyword: {expected_keyword}",
    }

result = keyword_evaluator(
    run_output="LangSmith improves observability for LLM apps.",
    expected_keyword="observability",
)

print(result)
```

This is simplistic, but good for format checks and hard constraints.

## LLM Judge Example

```python
from openai import OpenAI

client = OpenAI()

def judge_answer(question: str, answer: str, reference: str) -> str:
    prompt = f"""
    You are grading an answer.
    Question: {question}
    Candidate answer: {answer}
    Reference answer: {reference}

    Return one of: PASS, FAIL
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
```

Use this carefully:

- the judge can hallucinate
- grading may vary by model version
- prompts for grading need testing too

## A Better Production Strategy

Use a layered evaluation strategy:

1. deterministic checks for schema and tool correctness
2. heuristic checks for citations, forbidden content, or keywords
3. LLM judge for nuanced quality
4. human review for critical workflows

## Experimentation Patterns

Typical experiments:

- prompt A vs prompt B
- model A vs model B
- retriever chunk size 512 vs 1024
- top-k = 5 vs top-k = 10
- with reranker vs without reranker

Important principle:

Only change one major variable at a time if you want interpretable results.

## Example: Prompt Comparison

Prompt V1:

- "Answer the question."

Prompt V2:

- "Answer only from retrieved context. If context is missing, say you do not know."

Expected outcome:

- V2 usually lowers hallucination
- V2 may reduce recall or make answers shorter

This is a classic tradeoff interviewers like to discuss.

## Metrics That Matter in Real Systems

For a support assistant:

- answer acceptance rate
- ticket deflection rate
- escalation rate
- hallucination complaints
- average latency
- average tokens per request

For a code assistant:

- compile success
- test pass rate
- edit acceptance rate
- user follow-up correction rate

For a retrieval assistant:

- citation accuracy
- source coverage
- groundedness score
- stale document rate

## Real-World Failure Modes

### 1. Benchmark overfitting

The team keeps improving one dataset, but real production quality drops.

Fix:

- refresh datasets regularly
- include hidden holdout sets
- sample real traffic

### 2. Judge drift

The LLM judge changes behavior when the model behind it changes.

Fix:

- pin judge model versions when possible
- benchmark the judge itself
- keep human-labeled anchor sets

### 3. Misleading aggregate scores

Average quality rises, but enterprise finance queries break badly.

Fix:

- slice results by customer type, language, domain, and workflow

### 4. Good evals, bad UX

Answers are correct but too slow or too verbose.

Fix:

- include latency and user satisfaction in eval criteria

## What Interviewers Want to Hear

If asked "How would you evaluate an LLM system?" a strong answer is:

> I would build a representative dataset from production traffic and failure cases, define task-specific metrics like correctness, groundedness, tool accuracy, latency, and cost, and run offline experiments for every prompt or model change. For high-risk flows I would combine deterministic checks, LLM judges, and human review. In production I would also collect user feedback and watch slices, not just overall averages, because regressions often affect one segment first.

## Summary

Evaluation turns LLM development from guesswork into engineering.

If tracing tells you what happened, evaluation tells you whether the system is getting better.
