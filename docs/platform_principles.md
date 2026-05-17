# Platform Principles

## Zentory is an operating system, not a chatbot

The user can interact through Telegram, API or dashboard, but those surfaces are not the product boundary. The platform boundary is the operational workflow that observes business data, detects deviations, proposes safe actions and records outcomes.

## Human owner remains in control

Zentory can analyze, prioritize and recommend. Risky operations must go through approval. The platform must never hide a dangerous action behind a conversational interface.

## Mock-first until integrations are proven safe

Current MVP behavior is mock-only. Wildberries, Ozon, Yandex Market, Telegram and LLM calls must stay behind integration boundaries. Real write actions require explicit production readiness, credentials, idempotency, audit and rollback contracts.

## Explain before action

Every recommendation must explain:

- what changed;
- why it matters;
- what action is proposed;
- which data supports it;
- what risk level and approval mode apply.

## Self-check before recommendation

Calculation-heavy modules must pass through a self-check layer before the recommendation is considered reliable. If self-check finds critical errors, the result must be marked as requiring human review.

## Audit everything

The platform records decisions, approvals, rejections, mock executions and rollbacks. Audit is a product requirement, not an implementation detail.

## Automate only measurable work

Automation is accepted only when the effect can be measured in time saved, revenue, margin, stock health, advertising efficiency or error reduction.
