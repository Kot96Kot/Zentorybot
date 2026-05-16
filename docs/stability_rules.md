# Правила стабильной работы Zentorybot

Zentorybot должен быть безопасной backend-платформой для автономной работы Telegram-интерфейса, агентов и будущих marketplace-интеграций. На этапе scaffold все внешние вызовы остаются mock и не отправляют реальные запросы в WB, Ozon, Яндекс Маркет или Telegram.

## 1. Логирование всех действий

- Каждое входящее событие Telegram логируется как `telegram_webhook_received`.
- Каждое решение Orchestrator логируется через audit-событие `orchestrator_decision`.
- Каждое действие Action Registry логируется как `action_registered`, `action_approved`, `action_rejected`, `action_executed`, `duplicate_action_blocked` или `safe_mode_blocked_execution`.
- Ошибки логируются структурированно: `error_type`, `detail`, `source`, `mock`.

## 2. Retry для внешних API

- Любой будущий вызов marketplace API должен идти через `RetryService`.
- Retry применяется только к временным ошибкам: timeout, 429, 5xx, сетевые сбои.
- Retry не должен повторять небезопасные write-операции без idempotency key.
- После исчерпания попыток выбрасывается `RetryExhaustedError`, а действие остается неисполненным.

## 3. Error handling

- Telegram webhook не должен валить приложение при ошибке агента или внутренней задачи.
- Webhook возвращает контролируемый payload со статусом `error`, `source` и `error_type`.
- Внутренние ошибки проходят через `handle_internal_error` и попадают в структурированный лог.

## 4. Audit log

- Audit log создается для всех действий агентов и Action Registry.
- Audit-событие должно содержать тип события, action id, action type, risk level, approval mode, status и idempotency key, если он есть.
- В текущей версии audit хранится in-memory и явно помечен как mock.
- В production audit должен храниться в PostgreSQL и быть неизменяемым append-only журналом.

## 5. Idempotency

- Каждое действие получает idempotency key из `action_type`, `title` и `payload`.
- Повторное выполнение действия с тем же ключом блокируется.
- При дубле система возвращает существующее действие и помечает payload флагом `idempotency_duplicate`.
- Idempotency обязателен для будущих операций `update_price`, `send_reply`, изменения ставок и участия в акциях.

## 6. Safe mode

- По умолчанию safe mode включен.
- В safe mode система только предлагает действия и создает audit log.
- Автоматическое применение действий запрещено, пока человек явно не подтвердил действие или пока не включен controlled auto mode для низкорисковых операций.
- Даже в controlled auto mode должны работать лимиты риска, idempotency и audit log.

## 7. Mock-only integrations

- В scaffold запрещены реальные API-вызовы.
- Все ответы интеграций должны содержать `mock: true`.
- Секреты не должны попадать в код, логи, тесты или документацию кроме названий переменных в `.env.example`.
