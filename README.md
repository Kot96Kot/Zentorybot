# Zentorybot

Zentorybot — backend-платформа формата **AI operating system** для продавцов на Wildberries, Ozon и Яндекс Маркете. Это не «просто Telegram-бот»: Telegram используется как control center, а бизнес-логика находится в API Layer, Orchestrator, доменных агентах, Decision Engine и Action Layer.

## Миссия

Снять с менеджера маркетплейсов повторяющиеся ежедневные действия: сбор отчетов, проверку остатков, контроль ДРР, подготовку контента, анализ акций, ответы покупателям, планирование отгрузок и создание задач. Человек остается владельцем бизнеса и утверждает рискованные решения, а Zentorybot выступает AI-командой операционного управления.

## Текущий статус MVP

Статус: **MVP scaffold / mock-only / safe mode**.

Готово:

- FastAPI backend с обязательными endpoint'ами.
- Telegram Control Center с mock webhook обработкой.
- Простая web-панель `/dashboard` на FastAPI + Jinja2 для визуализации mock AI-агентов.
- Orchestrator и 11 доменных агентов.
- Decision Engine с risk levels и approval modes.
- Action Registry с audit, idempotency и safe mode.
- Доменные MVP-модули: план продаж, реклама, остатки/подсорты, акции, контент карточек.
- AI Team orchestration roles: Marketplace Manager, Analyst, Ads Manager, Content Director, CFO, Supply Manager, COO, Human Owner.
- Mock-интеграции WB/Ozon/Яндекс Маркет/Telegram без реальных API-вызовов.
- SQLAlchemy/Alembic scaffold, Docker Compose, Makefile, CI, unit/integration tests.

Не готово:

- Реальная авторизация и API-интеграции маркетплейсов.
- Реальный Telegram Bot API.
- Реальный LLM provider.
- Production persistence для Action Registry/Audit/Idempotency.
- Background workers в production-режиме.

## Главная архитектурная идея

```text
Telegram -> API Layer -> Orchestrator -> Agents -> Decision Engine -> Actions
```

- **Telegram** — интерфейс управления, команд, отчетов, approve/reject.
- **API Layer** — FastAPI-приложение и HTTP routers.
- **Orchestrator** — выбирает агента или AI-role workflow.
- **Agents** — доменные модули менеджера маркетплейсов.
- **Decision Engine** — риск, approval mode и политики безопасности.
- **Actions** — proposed actions, approval, reject, mock execute.
- **Integrations** — mock adapters WB/Ozon/Яндекс Маркет/Telegram.

## 11 функций менеджера, превращенных в агентов

1. План продаж — `SalesPlanAgent`.
2. Анализ конкурентов — `CompetitorAgent`.
3. Юнитка и ценообразование — `UnitEconomicsAgent`.
4. Контент карточек — `ContentAgent`.
5. Внутренняя реклама и ставки — `AdsAgent`.
6. Акции — `PromoAgent`.
7. Отгрузки и подсорты — `InventoryAgent`.
8. Запуск новинок — `LaunchAgent`.
9. Отзывы и общение с покупателями — `FeedbackAgent`.
10. Аналитика площадки и тренды — `AnalyticsAgent`.
11. Новые продукты и категорийка — `CategoryAgent`.

## Telegram Control Center

Поддерживаемый минимальный набор MVP-команд:

- `/start`
- `/help`
- `/daily`
- `/alerts`
- `/sku <sku>`
- `/plan`
- `/approve <action_id>`
- `/reject <action_id>`
- `/rollback <action_id>`
- `/status`

Пользователь не выбирает агента вручную: Orchestrator сам выбирает нужный mock-модуль. Telegram webhook работает в mock mode: реальные сообщения не отправляются, а `TelegramClient` возвращает `mock: true`.

## HTTP Endpoints

- `GET /health` — healthcheck, возвращает `{"status":"ok"}`.
- `GET /ready` — readiness check.
- `POST /telegram/webhook` — mock Telegram webhook и control center.
- `POST /actions/preview` — preview proposed actions.
- `POST /actions/approve` — approve action через API.
- `GET /reports/daily` — mock daily report.
- `GET /dashboard` — web-панель состояния AI-агентов.
- `GET /dashboard/alerts` — mock-алерты, требующие внимания.
- `GET /dashboard/actions` — proposed actions и approvals.
- `GET /dashboard/sku/{sku}` — mock-карточка SKU.
- `GET /dashboard/agents` — состояние агентов.
- `GET /dashboard/audit` — mock audit log.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
make dev
```

Проверка:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/reports/daily
# Dashboard: откройте http://localhost:8000/dashboard в браузере
curl -X POST http://localhost:8000/telegram/webhook \
  -H 'Content-Type: application/json' \
  -d '{"text":"/daily","chat_id":"1"}'
```

## Makefile-команды

- `make install` — установка проекта и dev-зависимостей.
- `make dev` — локальный запуск FastAPI через Uvicorn.
- `make test` — запуск pytest.
- `make lint` — запуск Ruff.
- `make format` — форматирование и автоисправления Ruff.
- `make docker-up` — запуск app + PostgreSQL + Redis.
- `make docker-down` — остановка docker compose.

## Структура проекта

```text
src/zentory/app              # FastAPI app factory и lifespan
src/zentory/api              # HTTP routers и dependencies
src/zentory/agents           # 11 доменных агентов, Orchestrator, team roles
src/zentory/decision         # Risk scoring, policies, approvals
src/zentory/actions          # Action schema и registry
src/zentory/schemas          # Pydantic-схемы доменных модулей
src/zentory/services         # бизнес-сервисы, audit, retry, idempotency, safe mode
src/zentory/integrations     # mock adapters Telegram/WB/Ozon/Yandex Market
src/zentory/db               # SQLAlchemy base, session, models
src/zentory/web              # Jinja2 dashboard, templates, static CSS
docs                         # продуктовая и архитектурная документация
prompts                      # prompt-шаблоны для будущих LLM-провайдеров
tests                        # unit и integration тесты
```

## Безопасный режим

- Секреты не хранятся в коде и описаны только как имена переменных в `.env.example`.
- Все внешние интеграции возвращают mock-данные.
- Реальных API-вызовов WB/Ozon/Яндекс Маркет/Telegram/OpenAI нет.
- Все write-like действия проходят через proposed actions.
- `LOW` -> `NONE`, `MEDIUM` -> `SOFT_APPROVAL`, `HIGH/CRITICAL` -> `HARD_APPROVAL`.
- Safe mode запрещает автоматическое применение действий.
- Idempotency защищает от повторного исполнения одного действия.

## Документация

- `docs/architecture.md` — архитектура платформы.
- `docs/telegram_control_center.md` — Telegram control center.
- `docs/dashboard.md` — простая web-панель для визуализации AI-агентов.
- `docs/action_center.md` — центр подтверждения действий AI-агентов.
- `docs/sku_intelligence_card.md` — единая карточка анализа товара по SKU.
- `docs/ai_team_structure.md` — AI-команда и роли.
- `docs/mvp_status.md` — финальный статус MVP.
- `docs/next_steps.md` — следующий план развития.
- `docs/*_module.md` — документация по доменным модулям.
