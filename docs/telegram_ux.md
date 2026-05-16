# Telegram UX

Zentorybot uses a minimal Telegram control interface. The user never chooses an agent manually: they send a business command, and the Orchestrator selects the mock module that should answer.

## Commands

| Command | Purpose |
| --- | --- |
| `/start` | Start the mock control center. |
| `/help` | Show the minimal command list. |
| `/daily` | Return yesterday's report and key deviations. |
| `/alerts` | Return only items that require management attention. |
| `/sku <sku>` | Build one SKU card with product card, sales, stock, ads, reviews, and recommendations. |
| `/plan` | Return today's action plan. |
| `/approve <action_id>` | Approve a proposed action. |
| `/reject <action_id>` | Reject a proposed action. |
| `/rollback <action_id>` | Roll back an action if a mock rollback plan exists. |
| `/status` | Show agent readiness and Safety Core status. |

## Message format

Telegram messages are short and managerial. Each command response uses the same structure:

1. **Статус** — what happened now.
2. **Проблема** — what needs attention.
3. **Причина** — why it happened.
4. **Рекомендация** — what the manager should do next.
5. **Риск** — `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
6. **Кнопки** — mock action commands such as `/plan`, `/alerts`, `/approve <action_id>`, `/reject <action_id>`.

## Mock behavior

- No real Telegram API is called.
- No real marketplace API is called.
- No real prices, bids, stock, or product cards are changed.
- Approval, rejection, rollback, and cards are represented by mock in-memory services.
- Safety Core remains the execution guard for proposed actions.

## Orchestrator routing

The Telegram layer maps commands to business event types only. The Orchestrator owns routing:

- `/daily` -> daily business summary.
- `/alerts` -> urgent cross-module alerts.
- `/sku <sku>` -> SKU overview with card, sales, stock, ads, reviews, and recommendations.
- `/plan` -> today's management plan.
- `/status` -> agent and Safety Core status.

This keeps Telegram simple while preserving a modular backend.
