# MVP Demo Checklist

Date: 2026-05-16  
Status: **MVP demo ready with environment caveats; mock-only; real APIs forbidden**.

## 1. README

| Check | Status | Evidence |
| --- | --- | --- |
| Real structure described | ✅ | README lists `src/zentory/app`, `api`, `agents`, `decision`, `actions`, `schemas`, `services`, `integrations`, `db`, `web`, `docs`, `prompts`, `tests`. |
| Run commands present | ✅ | README includes quick start and Makefile commands. |
| Mock mode described | ✅ | README states Telegram and marketplace integrations are mock-only. |
| Real API warning present | ✅ | README warns that real APIs are not connected. |
| Safety Core described | ✅ | README and `docs/safety_core.md` describe risk/approval/audit guards. |
| Action Center described | ✅ | README and `docs/action_center.md` describe action lifecycle. |
| Telegram UX described | ✅ | README and `docs/telegram_ux.md` list supported commands. |
| Dashboard described | ✅ | README and `docs/dashboard.md` list dashboard pages. |

## 2. Documentation

| Document | Status | Notes |
| --- | --- | --- |
| `docs/full_code_audit.md` | ✅ updated | Current final audit and command/API/security status. |
| `docs/fix_report.md` | ✅ created | Fixes, environment blockers and must-fix list. |
| `docs/business_logic_audit.md` | ✅ current | 33 business rules audited; 12 known strict `xfail` gaps. |
| `docs/safety_core.md` | ✅ reviewed | Explains Safety Core, rules and mock behavior. |
| `docs/action_center.md` | ✅ reviewed | Explains lifecycle and HTTP API. |
| `docs/telegram_ux.md` | ✅ reviewed | Matches supported command set. |
| `docs/dashboard.md` | ✅ reviewed | Matches server-rendered dashboard pages. |
| `docs/next_steps.md` | ✅ reviewed | Next steps remain accurate for real integrations. |

## 3. Make commands

| Command | Status | Result |
| --- | --- | --- |
| `make install` | ⚠️ blocked | Cannot fetch `hatchling`: package index tunnel returns 403. |
| `make dev` | ⚠️ blocked | `uvicorn` missing because install is blocked. |
| `make test` | ⚠️ blocked | `fastapi` and `pydantic` missing, so pytest collection fails. |
| `make lint` | ✅ passed | `ruff check .` passes. |
| `make docker-up` | ⚠️ blocked | `docker` binary is unavailable. |
| `make docker-down` | ⚠️ blocked | `docker` binary is unavailable. |

## 4. API readiness

Runtime HTTP smoke tests require installed dependencies. Route definitions were verified statically.

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /health` | ✅ declared | Returns `status: ok`. |
| `GET /ready` | ✅ declared | Returns `status: ready`. |
| `POST /telegram/webhook` | ✅ declared | Mock command parser + Orchestrator + mock Telegram client. |
| `POST /actions/preview` | ✅ declared | Orchestrator preview compatibility route. |
| `POST /actions/approve` | ✅ declared | ActionRegistry approval compatibility route. |
| `GET /reports/daily` | ✅ declared | Mock daily report. |

## 5. Security and safety

| Check | Status | Notes |
| --- | --- | --- |
| No secrets committed | ✅ | Regex scan found no private keys/common API tokens. |
| No real marketplace calls | ✅ | Marketplace clients return mock payloads only. |
| No real Telegram sends | ✅ | Telegram client returns `mock: true`, `status: not_sent`. |
| Integrations mock mode | ✅ | Auth configs default to `mock_mode=True`; clients return mock data. |
| Risky actions through approval | ⚠️ partial | SafetyEngine handles known action types; business audit lists gaps before real APIs. |
| Actions write audit log | ⚠️ partial | SafetyEngine and Action Center lifecycle write audit logs; some text-only recommendations are not Action Center actions yet. |

## 6. Tests and checks

| Command | Status | Result |
| --- | --- | --- |
| `pytest` | ⚠️ blocked | Fails during collection due missing `fastapi` and `pydantic`. |
| `ruff check .` | ✅ passed | Static lint passes. |
| `python -m compileall src` | ✅ passed | Source syntax compiles. |

## Project status

**Ready for MVP demo in mock-only mode.** The repository can demonstrate architecture, API shape, Telegram UX, dashboard UX, Action Center lifecycle, mock integrations and Safety Core concepts once dependencies are installed.

## Not ready

- Production persistence.
- Real marketplace reads/writes.
- Real Telegram Bot API.
- Real LLM provider.
- Autonomous or semi-autonomous write actions.
- Full test execution in this environment until dependencies are installable.

## Forbidden before safety fixes

- Real price updates.
- Real ad bid / budget / campaign pause updates.
- Real promo participation.
- Real content publishing or bulk edits.
- Real feedback/question replies.
- Any HIGH/CRITICAL action execution from Action Center without enforced hard approval and idempotency.

## Next best step

Run `make install`, `ruff check .`, `pytest` and FastAPI smoke tests in a dependency-complete environment. Then fix the strict `xfail` business-logic gaps before enabling any real external API integration.
