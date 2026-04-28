# Human-in-the-Loop and Durable Execution

## Why Human-in-the-Loop Matters

Some LLM workflows should not run fully autonomously.

Examples:

- issuing refunds
- approving compliance decisions
- changing permissions
- drafting legal or medical outputs
- triggering infrastructure actions

In such cases, a strong system pauses and asks for human review.

## Human-in-the-Loop Pattern

Typical flow:

```text
analyze_request
   |
   v
prepare_action
   |
   v
human_approval
   |
   +--> approved -> execute
   |
   +--> rejected -> revise_or_abort
```

This is easier to model in LangGraph than in a plain chain.

## Example State

```python
from typing import TypedDict, Optional

class ApprovalState(TypedDict):
    request: str
    proposed_action: str
    approved: Optional[bool]
    reviewer_comment: Optional[str]
    final_result: Optional[str]
```

## Example Approval Logic

```python
def check_if_approval_needed(state: ApprovalState) -> str:
    if "refund" in state["request"].lower():
        return "human_approval"
    return "execute_action"
```

This pattern is interview-relevant because it shows you know autonomy should be bounded.

## What is Durable Execution?

Durable execution means the workflow can:

- persist its progress
- survive crashes or restarts
- pause and resume later
- continue from a checkpoint

This is critical for:

- long-running workflows
- asynchronous human approvals
- multi-step agents
- workflows depending on slow external systems

## Why Durable Execution Matters

Without durability:

- a process restart may lose workflow state
- long-running jobs may need to start over
- approval workflows become brittle
- operators cannot safely resume failed runs

## Checkpoints

Checkpoints are saved snapshots of workflow state.

Typical checkpoint moments:

- before human approval
- after expensive retrieval or tool steps
- before side-effectful actions
- after every graph transition in critical flows

## Real-World Example: Refund Approval

Flow:

1. classify request
2. fetch order info
3. compute refund eligibility
4. checkpoint
5. wait for human approval
6. resume
7. issue refund or deny

This is much safer than rerunning the whole workflow after approval arrives.

## Real-World Example: Incident Response Assistant

Flow:

1. collect alerts
2. fetch logs
3. summarize likely root causes
4. ask human whether to run remediation
5. if yes, execute remediation step

Here, durable execution matters because:

- humans may respond later
- external systems may be flaky
- you must preserve audit context

## Design Principles

### 1. Keep approval state explicit

Do not hide approval in prompt text alone.

Track:

- who approved
- when
- what was approved
- what input state existed at approval time

### 2. Checkpoint before side effects

If the system is about to:

- send money
- mutate data
- trigger infrastructure changes

save state first.

### 3. Make resume behavior deterministic

On resume, the graph should know exactly:

- current node
- prior results
- remaining steps

### 4. Preserve auditability

Approval workflows should be explainable later.

## Common Failure Modes

### 1. Approval without enough context

Human reviewer sees only a short summary, not the evidence behind it.

Fix:

- include supporting docs, tool outputs, and rationale

### 2. Restart loses progress

The app crashes and the workflow restarts from the beginning.

Fix:

- use durable checkpoints
- store workflow state externally

### 3. Duplicate side effects after resume

The workflow resumes and repeats an action like issuing a refund.

Fix:

- idempotency keys
- explicit action-completed flags
- write-ahead audit state

### 4. Human bottleneck

Too many workflows pause for manual approval and backlog grows.

Fix:

- risk-based approvals
- automate low-risk cases
- prioritize review queues

## Strong Interview Answer

> I use human-in-the-loop patterns when the workflow has meaningful business, legal, financial, or operational risk. LangGraph is useful because it lets me make the approval step explicit in the workflow and combine it with durable execution, so the system can pause, persist state, and resume safely instead of relying on brittle in-memory agent loops.

## Summary

Human-in-the-loop adds control.
Durable execution adds resilience.

Together they make long-running or high-risk LLM workflows much safer to operate.
