# Action Lifecycle

Actions are the bridge between agent recommendations and marketplace operations. Zentory must treat actions as controlled operational records, not chat replies.

## Lifecycle

```text
Detected signal → Proposed action → Self-check → Approval decision → Mock/real execution → Audit → Outcome learning
```

## Stages

1. **Detected signal** — an agent or workflow finds a deviation or opportunity.
2. **Proposed action** — the platform creates a structured action with title, explanation, risk level, approval mode, evidence and before/after context.
3. **Self-check** — calculations and rule checks validate the proposed action. Failed checks must be visible to the human owner.
4. **Approval decision** — the owner approves or rejects according to risk level and safety mode.
5. **Execution** — in the current MVP, execution is mock-only. Real marketplace write calls are not allowed.
6. **Audit** — action creation, approval, rejection, execution skip, execution and rollback attempts are recorded.
7. **Outcome learning** — after execution, the platform should compare expected and actual effects.

## Non-negotiable contracts

- Actions must be idempotent.
- Rejected actions must not execute.
- Risky actions must require the appropriate approval.
- Every action must be auditable.
- Real external writes must stay disabled until production safety contracts are complete.
