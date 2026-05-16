# AI-команда Zentorybot

AI-команда — это слой orchestration roles поверх существующих агентов. Это пока не LLM-агенты: роли объединяют уже созданные доменные агенты, возвращают понятный результат и показывают, какие действия можно делать без approval, а какие только через approval.

## 1. AI Marketplace Manager

- Зона ответственности: ежедневная операционка, приоритеты роста, координация AI-команды.
- Входные данные: sales plan, daily analytics, alerts, цели владельца.
- Выходной результат: daily action plan, приоритеты SKU, сводка для владельца.
- Агенты: `SalesPlanAgent`, `AnalyticsAgent`.
- Telegram-команды: `/daily`, `/sales_plan`, `/alerts`, `/status`.
- Без approval: собрать digest, показать статус, создать задачу на анализ.
- Только через approval: изменить бюджет, утвердить план продаж, применить risky action.

## 2. AI Analyst

- Зона ответственности: аналитика продаж, тренды, конкуренты, причины отклонений.
- Входные данные: sales history, competitors, category trends, marketplace analytics.
- Выходной результат: аналитический отчет, гипотезы, объяснение отклонений.
- Агенты: `AnalyticsAgent`, `CompetitorAgent`, `CategoryAgent`.
- Telegram-команды: `/daily`, `/agents`, `/alerts`.
- Без approval: собрать отчет, найти аномалии, сформировать гипотезу.
- Только через approval: утвердить стратегическую гипотезу, запустить эксперимент.

## 3. AI Ads Manager

- Зона ответственности: внутренняя реклама, ДРР, CTR, ставки, алерты.
- Входные данные: ads metrics, margin, stock days, sales plan.
- Выходной результат: рекомендации по ставкам, critical alerts, список кампаний для проверки.
- Агенты: `AdsAgent`.
- Telegram-команды: `/ads_today`, `/alerts`.
- Без approval: собрать отчет, подсветить высокий ДРР, создать alert.
- Только через approval: изменить ставку, поставить кампанию на паузу, увеличить бюджет.

## 4. AI Content Director

- Зона ответственности: draft-контент, SEO, карточки, отзывы и вопросы.
- Входные данные: content brief, reviews, questions, CTR, competitor content.
- Выходной результат: draft карточки, ТЗ на фото/инфографику, задачи по отзывам.
- Агенты: `ContentAgent`, `FeedbackAgent`.
- Telegram-команды: `/content_new`, `/alerts`.
- Без approval: создать draft, подготовить ТЗ, сформировать черновик ответа.
- Только через approval: опубликовать контент, отправить ответ покупателю, изменить карточку.

## 5. AI CFO

- Зона ответственности: прибыль, маржа, цены, акции, финансовые ограничения.
- Входные данные: unit economics, promo terms, ad spend, commission, cost price.
- Выходной результат: price guard, promo decision, margin risk report.
- Агенты: `UnitEconomicsAgent`, `PromoAgent`.
- Telegram-команды: `/unit`, `/promo_check`, `/promo_list`.
- Без approval: рассчитать юнитку, найти риск по марже, собрать dangerous SKU.
- Только через approval: изменить цену, участвовать в акции, согласовать минимальную маржу.

## 6. AI Supply Manager

- Зона ответственности: остатки, out-of-stock, поставки, подсорты по складам.
- Входные данные: stocks, sales velocity, warehouse stock, transit, supply plan.
- Выходной результат: OOS risk list, replenishment plan, warehouse redistribution tasks.
- Агенты: `InventoryAgent`.
- Telegram-команды: `/stocks`, `/stock_risks`, `/replenishment`.
- Без approval: создать stock alert, рассчитать покрытие, найти slow mover.
- Только через approval: создать поставку, перераспределить склад, изменить рекламный статус SKU.

## 7. AI COO

- Зона ответственности: операционная надежность, SLA, approval queue, alerts, safe mode.
- Входные данные: audit log, action registry, alerts, agent statuses, retry queue.
- Выходной результат: операционный статус, очередь approvals, risk dashboard.
- Агенты: `AnalyticsAgent`, `AdsAgent`, `InventoryAgent`.
- Telegram-команды: `/status`, `/alerts`, `/agents`, `/agent_status`.
- Без approval: показать статус, собрать alerts, проверить агентов.
- Только через approval: разрешить controlled auto, закрыть critical incident, обойти safe mode.

## 8. Human Owner

- Зона ответственности: стратегия, бюджет, risk appetite, финальные решения.
- Входные данные: все отчеты AI-команды, approval cards, финансовые ограничения.
- Выходной результат: approved/rejected actions, стратегические решения, лимиты риска.
- Агенты: все роли AI-команды как advisory слой.
- Telegram-команды: `/approve <action_id>`, `/reject <action_id>`, `/daily`, `/status`.
- Без approval: смотреть отчеты, получать alerts, задавать цели.
- Только через approval: любые изменения бюджета, цены, рекламы, поставок, публикаций и акций.
