# Next steps

## 1. Подготовить окружение зависимостей

- Зафиксировать lockfile (`uv.lock` или аналог).
- Проверить `make install` в network-enabled окружении.
- Запустить полный `pytest` в CI.
- Добавить smoke-test запуска FastAPI.

## 2. Перевести in-memory сервисы на PostgreSQL

- Action Registry persistence.
- Audit log append-only storage.
- Idempotency keys table.
- Telegram command/event history.

## 3. Подключить read-only marketplace APIs

Порядок подключения:

1. Stocks.
2. Orders/sales.
3. Prices.
4. Reviews/questions.
5. Ads stats.
6. Promo terms.

Все подключения сначала в shadow mode без write-действий.

## 4. Подключить реальный Telegram Bot API

- Webhook secret validation.
- Real sendMessage.
- Inline keyboards approve/reject.
- User/tenant mapping.
- Command permissions.

## 5. Подключить real LLM provider

- Оставить `MockContentLLMProvider` как fallback.
- Добавить provider interface для OpenAI/других моделей.
- Включить prompt/version audit.
- Добавить guardrails для маркетплейс-ограничений.

## 6. Включать write-actions постепенно

- Stage 1: только draft/recommendations.
- Stage 2: assisted mode с manual copy.
- Stage 3: semi-auto mode через HARD_APPROVAL.
- Stage 4: controlled auto только для low-risk actions с лимитами.

## 7. Production hardening

- Auth, tenants, roles.
- Secrets manager.
- Rate limiting.
- Error budgets.
- Monitoring.
- Backup/restore.
- Marketplace sandbox checks.

## 8. MVP demo gate checklist

Before demo in a normal dependency-complete environment:

1. Run `make install`.
2. Run `ruff check .`.
3. Run `pytest`.
4. Start `make dev`.
5. Smoke-check `GET /health`, `GET /ready`, `GET /reports/daily`, `POST /telegram/webhook`, `POST /actions/preview`.
6. Open `/dashboard` and `/dashboard/actions`.
7. Keep all real APIs disabled and use `.env.example` as names-only reference.

Before real API work, resolve the must-fix list in `docs/business_logic_audit.md` and `docs/mvp_demo_checklist.md`.
