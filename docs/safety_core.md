# Safety Core

Safety Core is the mock-only guardrail layer that must run before any marketplace agent action is executed. It does not call real marketplace APIs and does not mutate prices, bids, content cards, inventory, or promotions.

## Goal

No agent action may be executed until Zentorybot has:

1. evaluated action risk;
2. checked operational limits;
3. determined whether approval is required;
4. written the proposed action and safety decision to the audit log.

## Modules

- `zentory.decision.risk_levels` defines risk ordering helpers for `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL`.
- `zentory.decision.approval_modes` defines automation modes: `SHADOW`, `ASSISTANT`, `SEMI_AUTO`, and `AUTO`.
- `zentory.actions.action_limits` stores configurable mock limits for price changes, bid increases, promotion margin, and stock-days guards.
- `zentory.decision.safety_rules` evaluates action-specific rules.
- `zentory.decision.safety_engine` combines rules, automation mode policy, approval requirements, and audit logging.
- `zentory.services.rollback_service` stores mock rollback plans for future integrations.
- `zentory.services.audit_service` stores in-memory mock audit records for every evaluated action.

## Automation modes

| Mode | Behavior |
| --- | --- |
| `SHADOW` | Records what the system would do. It never executes an action. |
| `ASSISTANT` | Proposes actions for a human. It never executes an action. |
| `SEMI_AUTO` | Executes only `LOW` risk actions with no approval requirement. `MEDIUM` and higher require approval. |
| `AUTO` | Executes only actions that are inside limits and have no approval requirement. |

## Rules implemented

1. `SHADOW` mode only logs what would happen.
2. `ASSISTANT` mode proposes actions but does not execute them.
3. `SEMI_AUTO` mode allows automatic execution only for `LOW` risk actions.
4. `AUTO` mode allows execution only when limits are satisfied.
5. `HIGH` and `CRITICAL` risk always require hard approval.
6. Price changes greater than 5% require approval.
7. Ad bid increases greater than 10% require approval.
8. Promotion participation below the minimum margin is forbidden and marked `CRITICAL`.
9. If stock is below 7 days, ad strengthening is forbidden and marked `CRITICAL`.
10. Every proposed action evaluated by `SafetyEngine` creates an audit log entry.

## Example mock action

```python
from zentory.actions.schemas import Action
from zentory.decision.approval_modes import AutomationMode
from zentory.decision.safety_engine import SafetyEngine

engine = SafetyEngine(mode=AutomationMode.AUTO)
action = Action(
    action_type="price_change",
    title="Raise price",
    description="Mock-only price change",
    payload={"change_percent": 3},
)
decision = engine.evaluate(action)
assert decision.allowed_to_execute is True
```

The example evaluates a mock action only. A future real integration must still use the safety decision and audit trail before calling external APIs.

## MVP demo verification (2026-05-16)

Safety Core is sufficient for **mock-only MVP demo** because it demonstrates risk levels, approval modes, limit checks and audit logging without calling external APIs.

Before real APIs are connected, the following gaps must be closed:

- price changes must validate minimum margin, cost price and mandatory expenses;
- price changes above 15% must require hard approval;
- content publish and bulk content updates need dedicated safety rules;
- feedback replies need negative/legal/warranty/return classification and knowledge-base grounding;
- bulk promo participation needs hard approval rules;
- Action Center execution must enforce idempotency and HIGH/CRITICAL approval consistency.
