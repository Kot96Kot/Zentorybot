# MVP status

Дата проверки: 2026-05-16.

## Статус

Zentorybot находится в состоянии **MVP scaffold / mock-only / safe mode**. Проект содержит backend-платформу, Telegram control center, доменных агентов, AI-team roles, Decision Engine, Action Registry, mock-интеграции, документацию, Docker/CI и тесты.

## Готово

### Backend

- FastAPI app factory.
- Lifespan logging.
- Routers: health, telegram, actions, reports.
- Обязательные endpoints:
  - `GET /health`
  - `GET /ready`
  - `POST /telegram/webhook`
  - `POST /actions/preview`
  - `POST /actions/approve`
  - `GET /reports/daily`

### Agents and orchestration

- 11 доменных агентов менеджера маркетплейсов.
- Orchestrator для выбора агента и регистрации actions.
- AI-team orchestration roles.
- Decision Engine для risk/approval.

### Domain MVP modules

- План продаж.
- Внутренняя реклама.
- Остатки, отгрузки и подсорты.
- Акции и unit profit.
- Контент карточки товара через mock LLM provider.
- Telegram Control Center.

### Safety

- Safe mode включен по умолчанию.
- Idempotency layer есть.
- Audit service есть.
- Retry service есть.
- Все интеграции работают в mock mode.
- Реальные API ключи не используются.

### Tooling

- `Makefile`.
- `Dockerfile`.
- `docker-compose.yml` с app/postgres/redis.
- GitHub Actions CI.
- Alembic scaffold.
- `.env.example` без секретов.

## Проверки финальной сборки

| Проверка | Статус в текущем окружении | Комментарий |
|---|---|---|
| `ruff check .` | pass | Статический анализ проходит. |
| `python -m compileall -q src tests` | pass | Синтаксис Python-файлов валиден. |
| `python -m pytest` | blocked | В текущем контейнере не установлены runtime deps (`fastapi`, `pydantic`) и PyPI недоступен. |
| `make install` | blocked | Требует доступа к PyPI для установки зависимостей. |
| `make dev` | blocked | В текущем контейнере нет `uvicorn`, так как runtime deps не установлены. |
| `make docker-down` / `make docker-up` | blocked | В текущем контейнере нет Docker CLI. |
| Endpoint runtime check | blocked | Нельзя поднять FastAPI без установленных runtime deps. |

## Не готово для production

- Реальные WB/Ozon/Яндекс Маркет API.
- Реальный Telegram Bot API.
- Реальный LLM provider.
- Persistent audit/action/idempotency storage.
- AuthN/AuthZ для владельцев и сотрудников.
- Rate limits, quotas и marketplace-specific retry policies.
- Production observability: metrics, traces, alerting.
