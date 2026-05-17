# Full Code Audit

Audit date: 2026-05-16  
Scope: final MVP demo readiness review of repository structure, docs, commands, public routes, mock integrations, Safety Core, Action Center and tests.

## Executive status

Zentorybot is **ready for MVP demo in mock-only mode**. It is suitable for showing the product architecture, Telegram UX, dashboard pages, proposed actions, approval/reject flows, mock domain agents and safety documentation.

It is **not ready for real marketplace writes**. Real WB/Ozon/Yandex Market/Telegram/LLM APIs must remain disconnected until the must-fix safety gaps listed below are closed.

## Verified structure

- FastAPI app factory: `src/zentory/app/main.py`.
- API routers: `src/zentory/api/routers/health.py`, `telegram.py`, `actions.py`, `reports.py`.
- Orchestrator and agents: `src/zentory/agents/`.
- Safety Core: `src/zentory/decision/`, `src/zentory/actions/action_limits.py`.
- Action Center and registry: `src/zentory/actions/`.
- Mock integrations: `src/zentory/integrations/`.
- Dashboard: `src/zentory/web/routes.py`, `src/zentory/web/templates/`, `src/zentory/web/static/`.
- Tests: `tests/unit/` and `tests/integration/`.
- Docs: `docs/`.

## Command checks

| Command | Result in current environment | Notes |
| --- | --- | --- |
| `make install` | **Blocked by environment** | pip cannot fetch build dependency `hatchling` because the package index tunnel returns 403. |
| `make dev` | **Blocked by missing dependency** | `uvicorn` is not installed because install is blocked. |
| `make test` / `pytest` | **Blocked by missing dependencies** | collection fails because `fastapi` and `pydantic` are not installed. |
| `make lint` / `ruff check .` | **Passed** | Static lint is available in the environment. |
| `make docker-up` | **Blocked by environment** | `docker` binary is not installed. |
| `make docker-down` | **Blocked by environment** | `docker` binary is not installed. |
| `python -m compileall src` | **Passed** | Source syntax compiles. |

## API route audit

Routes are declared in code and covered by tests, but runtime HTTP smoke checks are blocked in this environment until dependencies are installed.

| Route | Declared | Demo status |
| --- | --- | --- |
| `GET /health` | yes | returns `{"status": "ok"}` when app dependencies are installed. |
| `GET /ready` | yes | returns `{"status": "ready"}` when app dependencies are installed. |
| `POST /telegram/webhook` | yes | parses mock Telegram commands and routes through Orchestrator / mock Telegram client. |
| `POST /actions/preview` | yes | preview flow through Orchestrator / ActionRegistry compatibility path. |
| `POST /actions/approve` | yes | approves ActionRegistry action by id. |
| `GET /reports/daily` | yes | returns mock daily report. |

## Security and mock-mode audit

- Secret scan found no committed private keys, common API key patterns or Telegram token assignments.
- Marketplace clients expose read/write-like methods, but all return mock payloads and write methods return `status: "not_sent"`.
- Telegram client returns mock messages and does not call Telegram Bot API.
- `ActionExecutor` records `external_api_called: false` for mock execution and rollback.
- `.env.example` contains variable names only, not secrets.

## Safety findings

### Implemented enough for MVP demo

- SafetyEngine risk/approval decisions for known action types.
- Price-change approval above 5%.
- Ad-bid approval above 10% and stock-days block below 7 days.
- Promo margin / mandatory-cost checks in promo analysis.
- Inventory critical/warning thresholds and AdsAgent low-stock alerts.
- Action Center create/preview/approve/reject/execute/rollback mock lifecycle.
- Audit records for SafetyEngine decisions and Action Center lifecycle events.

### Must fix before real APIs

- Pricing economics guards are incomplete: minimum margin, cost price and mandatory expenses are not enforced for price changes.
- Price changes above 15% do not force hard approval.
- Content publish / bulk update safety policy is missing.
- Feedback replies are not classified for negative/legal/warranty/return risk and are not grounded in a knowledge base.
- Bulk promo participation does not require hard approval.
- Action Center execution is not idempotent and can trust caller-supplied `approval_mode` for HIGH/CRITICAL actions.
- Sales-plan ad/conversion recommendations are text recommendations, not guarded Action Center proposals.

## Demo verdict

**MVP demo can proceed only in mock mode.** Do not connect real write APIs, real Telegram sends, or real LLM autonomous publishing until the must-fix items are closed and full tests pass in a dependency-complete environment.
