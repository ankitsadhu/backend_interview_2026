# Structured Outputs

## Why Structured Outputs Matter

Backend systems need predictable data.

Free-form text is hard to parse safely.

Structured outputs are used for:

- extraction
- classification
- function calling
- workflow routing
- API payload generation
- data normalization

## Bad Pattern: Regex Over Model Text

```python
text = model("Extract name and age from this profile")
name = re.search(r"name: (.*)", text).group(1)
```

This breaks when the model changes formatting.

Better pattern:

```text
schema -> constrained or validated generation -> typed object
```

## Prompting vs JSON Mode vs Constrained Decoding

### Prompting

Ask the model to output JSON.

Pros:

- simple
- works with almost any model

Cons:

- can still produce invalid JSON
- may include extra prose

### JSON Mode

The model/runtime is biased or constrained to produce valid JSON.

Pros:

- better syntax reliability

Cons:

- valid JSON does not mean schema-correct JSON

### Schema-Constrained Decoding

The decoder restricts allowed next tokens based on a schema or grammar.

Pros:

- strongest format control
- useful for enums, required fields, nested objects

Cons:

- may increase latency
- implementation depends on model/runtime
- complex schemas can be tricky

Strong interview answer:

```text
Prompting asks nicely. JSON mode improves syntax. Constrained decoding enforces the allowed token space.
```

## First-Principles View of Constrained Decoding

Normal decoding chooses from many possible next tokens.

Constrained decoding masks invalid tokens.

Example:

```text
Expected schema: {"sentiment": "positive" | "negative"}

After generating {"sentiment":
allowed next values are constrained to known enum strings.
```

The model still decides among valid options, but the decoder prevents invalid syntax.

## Pydantic Validation Example

```python
from pydantic import BaseModel, Field, ValidationError


class TicketRoute(BaseModel):
    category: str = Field(pattern="^(billing|technical|security)$")
    priority: int = Field(ge=1, le=5)
    summary: str


def parse_ticket(payload: dict) -> TicketRoute:
    return TicketRoute.model_validate(payload)


try:
    ticket = parse_ticket({
        "category": "security",
        "priority": 5,
        "summary": "User reports suspicious login activity.",
    })
except ValidationError as exc:
    print(exc)
```

Validation is still needed even if the model usually behaves.

## Repair Loop Pattern

```python
def generate_with_validation(llm, prompt, schema, max_attempts=2):
    errors = None

    for _ in range(max_attempts):
        response = llm.invoke({
            "prompt": prompt,
            "schema": schema,
            "previous_errors": errors,
        })

        try:
            return schema.model_validate_json(response)
        except Exception as exc:
            errors = str(exc)

    raise ValueError("Could not produce valid structured output")
```

Production note:

```text
Repair loops should be capped. Infinite retries turn model uncertainty into latency incidents.
```

## Function Calling

Function calling is structured output with an action boundary.

The model does not execute the function by itself. It emits a structured call such as:

```json
{
  "name": "refund_order",
  "arguments": {
    "order_id": "ord_123",
    "reason": "duplicate charge"
  }
}
```

Your application validates and executes the call.

## Security Concerns

Structured output is not automatically safe.

You still need:

- schema validation
- authorization checks
- allowed tool lists
- idempotency for side effects
- human approval for risky actions
- audit logs

Interview trap:

```text
The model choosing a function is not permission to execute it.
```

## Common Failure Modes

- invalid JSON
- missing required fields
- wrong enum
- hallucinated fields
- unsafe tool arguments
- over-large outputs
- schema drift between prompt and backend
- partial streaming output parsed too early

## Cross Questions

### Is valid JSON enough?

No. It may be syntactically valid but semantically wrong or schema-invalid.

### Why not ask for CSV?

CSV is fragile for nested data, escaping, missing fields, and multi-line values. JSON with schema validation is usually safer.

### When would you use constrained decoding?

When downstream systems require high reliability, such as extraction, tool calls, workflow routing, compliance data, or production APIs.

### How do you evaluate structured output?

Measure:

- parse success rate
- schema validity
- field-level accuracy
- business-rule violations
- latency and retry rate

