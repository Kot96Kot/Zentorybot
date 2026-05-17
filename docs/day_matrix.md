# Матрица дня менеджера

## Утро

| Блок | Частота | Команда в Telegram | Агент | Результат | Подтверждение |
|---|---:|---|---|---|---|
| Отчет за вчера | ежедневно | `/daily` | AnalyticsAgent | digest продаж, алертов и задач | нет |
| Продажи | ежедневно | `/sales` | SalesPlanAgent | отклонение от плана | нет |
| Остатки | ежедневно | `/stocks` | InventoryAgent | SKU с риском дефицита | soft approval для задач поставки |
| Отзывы и вопросы | ежедневно | `/feedback` | FeedbackAgent | черновики ответов | hard approval для негатива |
| Алерты по ДРР | ежедневно | `/ads_alerts` | AdsAgent | кампании выше лимита | hard approval для ставок |
| Out-of-stock риски | ежедневно | `/oos` | InventoryAgent | список критичных SKU | soft approval |

## День

| Блок | Частота | Команда в Telegram | Агент | Результат | Подтверждение |
|---|---:|---|---|---|---|
| Реклама | 2-3 раза в день | `/ads` | AdsAgent | рекомендации по кампаниям | hard approval |
| Ставки | 2-3 раза в день | `/bids` | AdsAgent | предложения по ставкам | hard approval |
| Акции | по календарю | `/promo` | PromoAgent | оценка участия | hard approval |
| Контент | ежедневно | `/content` | ContentAgent | задачи на карточки | soft approval |
| Конкуренты | ежедневно | `/competitors` | CompetitorAgent | изменения конкурентов | нет |
| Подсорт | ежедневно | `/reorder` | InventoryAgent | приоритет поставки | soft approval |

## Вечер

| Блок | Частота | Команда в Telegram | Агент | Результат | Подтверждение |
|---|---:|---|---|---|---|
| Анализ дня | ежедневно | `/day_summary` | AnalyticsAgent | итоги дня | нет |
| Гипотезы | ежедневно | `/hypotheses` | CategoryAgent | список гипотез роста | нет |
| План действий на завтра | ежедневно | `/tomorrow` | SalesPlanAgent | action plan | soft approval |
| Отчет собственнику | ежедневно/еженедельно | `/owner_report` | AnalyticsAgent | короткий управленческий отчет | нет |
