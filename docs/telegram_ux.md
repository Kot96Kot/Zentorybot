# Telegram UX

Zentorybot uses Telegram as a **managerial control interface**, not as a menu of technical agents. The user does not choose `AdsAgent`, `InventoryAgent`, `ForecastABCAgent` or any other internal module. The user sends a business command, and the Orchestrator routes it to the right agent or service.

All responses are mock-only in the current MVP. No real Telegram, Wildberries, Ozon or Yandex Market API calls are made.

## Main commands

| Command | Purpose |
| --- | --- |
| `/start` | Start the mock control center. |
| `/help` | Show only the managerial command list. |
| `/daily` | Daily summary: sales, stock, ads, reviews, alerts and recommendations. |
| `/alerts` | Only what needs attention: critical signals, warnings and pending approvals. |
| `/sku <sku>` | Unified SKU card: sales, stock, ads, reviews, competitors, forecast and recommendations. |
| `/plan` | Day plan: what to check, approve, postpone and handle urgently. |
| `/approve <action_id>` | Approve a proposed action. |
| `/reject <action_id>` | Reject a proposed action. |
| `/rollback <action_id>` | Roll back an action when a mock rollback plan exists. |
| `/status` | Safety mode, agent status, mock mode and pending actions count. |

Manual commands for individual agents must not be shown in the main help. Forecast, ads, promo and inventory modules stay internal and are selected by Orchestrator.

## Message format

Every Telegram response should use the same managerial card shape:

1. **Статус** — what happened now.
2. **Проблема** — what needs attention.
3. **Причина** — why it happened.
4. **Рекомендация** — what the manager should do next.
5. **Риск** — `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
6. **Нужно подтверждение** — whether the next action needs approval.

Optional mock buttons can point to the next managerial command, for example `/plan`, `/alerts`, `/sku <sku>`, `/approve <action_id>` or `/reject <action_id>`.

## Command logic

### `/daily`

Returns a business summary with:

- sales;
- stock;
- ads;
- reviews;
- alerts;
- recommendations.

### `/alerts`

Returns only what requires attention:

- critical issues;
- warnings;
- pending approvals.

### `/sku <sku>`

Returns one SKU card with:

- sales;
- stock;
- ads;
- reviews;
- competitors;
- forecast;
- recommendations.

### `/plan`

Returns the day plan:

- what to check;
- what to approve;
- what to postpone;
- what is urgent.

### `/status`

Returns:

- safety mode;
- agent readiness;
- mock mode;
- pending actions count.

## Orchestrator routing

Telegram maps text to business event types only:

- `/daily` -> `daily`;
- `/alerts` -> `alerts`;
- `/sku <sku>` -> `sku_overview`;
- `/plan` -> `plan`;
- `/status` -> `control_status`.

The Orchestrator owns module selection and returns a mock managerial card.

## Mock behavior

- No real Telegram API is called.
- No real marketplace API is called.
- No real prices, bids, stock or product cards are changed.
- Approval, rejection, rollback and cards are represented by mock in-memory services.
- Safety Core remains the guard for proposed actions.
