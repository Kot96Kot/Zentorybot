# Telegram Control Center

Telegram Control Center — это интерфейс управления AI-командой Zentorybot. Telegram не содержит бизнес-логику: он принимает команду, нормализует payload и передает событие в Orchestrator. Orchestrator выбирает агента, агент возвращает рекомендации, Decision Engine выставляет риск и approval mode, а Telegram показывает сообщение или карточку действия с кнопками approve/reject.

## Команды

| Команда | Назначение | Событие |
|---|---|---|
| `/start` | Запуск control center | `control_start` |
| `/help` | Список команд | `control_help` |
| `/status` | Статус платформы | `control_status` |
| `/daily` | Ежедневный отчет | `daily` |
| `/sales_plan` | План продаж | `sales_plan` |
| `/ads_today` | Реклама за день | `ads_today` |
| `/stock_risks` | Риски out-of-stock | `stock_risks` |
| `/content_new` | Draft контента карточки | `content_new` |
| `/promo_check` | Проверка акций | `promo_check` |
| `/unit` | Юнит-экономика | `unit_economics` |
| `/alerts` | Общие алерты | `alerts` |
| `/approve <action_id>` | Подтвердить действие | `approve_action` |
| `/reject <action_id>` | Отклонить действие | `reject_action` |
| `/agents` | Список агентов | `control_agents` |
| `/agent_status` | Статус агентов | `control_agent_status` |

## Approval workflow

Если Decision Engine выставил `SOFT_APPROVAL` или `HARD_APPROVAL`, Telegram formatter создает карточку действия:

- название действия;
- риск;
- approval mode;
- action id;
- кнопки `/approve <action_id>` и `/reject <action_id>`.

## Mock mode

Реальный Telegram API не вызывается. `TelegramClient` сохраняет отправленные сообщения в in-memory список и возвращает `mock: true`.
