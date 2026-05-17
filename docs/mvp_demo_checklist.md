# MVP Demo Checklist

Date: 2026-05-17  
Status: **MVP demo ready / mock-only / safe mode**.

## What is ready

- FastAPI app with health, Telegram, actions, analytics, content, finance, learning, reports, SKU and supply routers.
- Telegram Control Center with mock webhook responses.
- Server-rendered dashboard for mock AI agent status, alerts, actions, SKU cards and audit.
- Orchestrator, domain agents, Decision Engine, Safety Engine, Action Registry and Action Center.
- Finance Checker and Learning Loop in deterministic mock mode.
- Mock WB/Ozon/Yandex/Telegram clients that do not call real APIs.
- CI configuration, Docker scaffold, Makefile, Alembic scaffold and test suite.

## Works only in mock mode

- Marketplace integrations.
- Telegram sends.
- Action execution and rollback.
- Finance reports, SKU cards, forecast, supply plans and Learning Loop data.
- Content generation provider.
- Dashboard data.

## Do not connect to real API yet

Do **not** enable real write APIs for:

- Price updates.
- Ad bid/budget/campaign changes.
- Promo participation.
- Content publishing or bulk edits.
- Review/question replies.
- Payments, payouts or finance report modifications.

Read-only WB API is the recommended next integration step, but it must start in SHADOW mode with mock fixtures kept for tests.

## Required Telegram commands

- `/daily`
- `/alerts`
- `/sku <sku>`
- `/plan`
- `/approve <action_id>`
- `/reject <action_id>`
- `/rollback <action_id>`
- `/status`
- `/abc`
- `/forecast`
- `/stock_risks`
- `/content_sku <sku>`
- `/finance_check`

Additional demo commands are also available: `/start`, `/help`, `/forecast_sku <sku>`, `/replenishment`, `/warehouses`, `/ctr_test`, `/content_brief`, `/pnl_check`, `/unit <sku>`, `/action_result <action_id>`, `/learning <sku>`.

## Required API endpoints

- `GET /health`
- `GET /ready`
- `POST /telegram/webhook`
- `GET /reports/daily`
- `GET /sku/{sku}/intelligence`
- `GET /analytics/abc`
- `GET /analytics/forecast`
- `GET /supply/risks`
- `GET /finance/check`
- `GET /learning/actions`

Useful demo endpoints:

- `GET /dashboard`
- `GET /dashboard/actions`
- `GET /dashboard/sku/{sku}`
- `POST /actions`
- `GET /actions`
- `GET /actions/pending`
- `POST /learning/action-result`
- `GET /learning/sku/{sku}`

## Safety checklist

- ✅ Risky actions require approval.
- ✅ HIGH and CRITICAL actions require HARD_APPROVAL.
- ✅ HIGH and CRITICAL actions do not execute automatically.
- ✅ Mock execution does not call marketplace APIs.
- ✅ No `.env` is tracked.
- ✅ `.env.example` is present.
- ✅ No real API tokens are required for demo.

## Tests and checks

Latest local verification:

- `ruff check .` — passed.
- `pytest` — passed: 189 collected, 186 passed, 3 xfailed.
- `python -m compileall src` — passed.

`tests/unit/test_mvp_demo_readiness.py` verifies the required endpoints, Telegram commands, and core safety/demo-secret guards.

## Next step: WB API connection

1. Add read-only Wildberries client methods for stocks and orders.
2. Keep current mock fixtures and add contract tests around normalized payloads.
3. Store real credentials outside git using environment/secret manager.
4. Route WB payloads through `DataNormalizationService`.
5. Run in SHADOW mode only.
6. Compare WB real read-only data with mock reports.
7. Only after audit/idempotency/persistence are production-ready, design separate write-action adapters.

## Demo operator rule

If a step would mutate marketplace state, send a Telegram message, publish content, change price, change ad spend or join promo in a real account — **do not run it in MVP demo**.
