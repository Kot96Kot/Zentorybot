# MVP status

Дата проверки: 2026-05-17.

## Статус

Zentorybot находится в состоянии **MVP demo ready / mock-only / safe mode**. Проект можно показывать как демонстрацию архитектуры, Telegram Control Center, Action Center, Decision/Safety Engine, dashboard, доменных агентов и mock-интеграций.

Реальные WB/Ozon/Яндекс Маркет/Telegram write API **не подключены** и не должны включаться до отдельного production safety review.

## Готово для demo

### Backend/API

- FastAPI app factory `create_app`.
- Routers: health, telegram, actions, analytics, content, finance, learning, reports, sku, supply.
- Проверенные MVP endpoints:
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

### Telegram UX

Проверены команды:

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

### Safety

- Risky Action Center actions are escalated to approval.
- HIGH and CRITICAL actions require HARD_APPROVAL and are not auto-executed.
- Known price, promo, content publication and bulk-change guards are covered by tests.
- Marketplace clients and Telegram client stay mock-only.
- No `.env` is tracked; `.env.example` is present.
- No secrets should be committed; real tokens belong in external secret storage.

### Tooling

- `Makefile` with install/dev/test/lint/format/docker commands.
- GitHub Actions CI runs install, `ruff check .`, and `pytest`.
- Dockerfile and docker-compose scaffold app/postgres/redis.
- Alembic scaffold is present for future persistence.

## Проверки финальной сборки

| Проверка | Статус | Результат |
|---|---:|---|
| `ruff check .` | ✅ pass | Static lint passed. |
| `pytest` | ✅ pass | 189 collected: 186 passed, 3 xfailed. |
| `python -m compileall src` | ✅ pass | Source files compile. |
| MVP endpoint smoke tests | ✅ pass | Covered by `tests/unit/test_mvp_demo_readiness.py`. |
| MVP Telegram command smoke tests | ✅ pass | Covered by `tests/unit/test_mvp_demo_readiness.py` and Telegram UX tests. |

## Ограничения MVP

- Persistence is in-memory for Action Registry/Action Center/Learning Loop/Audit in demo mode.
- External integrations are mock adapters only.
- LLM provider is mock-only for content generation.
- Background workers are scaffold stubs.
- SEMI_AUTO/AUTO modes are documented but not allowed for real write actions.

## Merge readiness

The repository is ready to merge as an MVP demo baseline if reviewers accept mock-only behavior and in-memory demo persistence.
