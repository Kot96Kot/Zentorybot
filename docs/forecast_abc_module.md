# Forecast & ABC Module

Forecast & ABC is a mock-only analytics module for ranking SKU importance and estimating stock needs. It does not call real marketplace APIs.

## ABC analysis

Supported metrics:

- `revenue`
- `profit`
- `sales_qty`

Rules:

1. SKU are sorted by selected metric in descending order.
2. `share = sku_metric / total_metric`.
3. `cumulative_share` is the running cumulative share.
4. `A`: `cumulative_share <= 80%`.
5. `B`: `cumulative_share > 80% and <= 95%`.
6. `C`: `cumulative_share > 95%`.

The API keeps both decimal fields (`share`, `cumulative_share`) and percent fields (`share_percent`, `cumulative_share_percent`) for readable dashboards and checks.

## Forecast

For every SKU the module calculates:

- `avg_daily_sales_7d`
- `avg_daily_sales_14d`
- `avg_daily_sales_30d`
- `forecast_sales_30`
- `forecast_sales_60`
- `forecast_sales_90`
- `stock_coverage_days`
- `recommended_replenishment_qty_30`
- `recommended_replenishment_qty_60`
- `recommended_replenishment_qty_90`

If `active_sales_days_*` is present, average daily sales is calculated by days with stock/sales availability. If active days are missing, the service falls back to calendar days and adds a warning.

## Seasonality

Seasonality is explicit and auditable:

- category coefficient;
- month coefficient;
- SKU-specific coefficient;
- trend coefficient clamped from `0.7` to `1.5`.

The final `seasonality_coefficient` is the product of category, month and SKU coefficients.

## Self-check

Self-check verifies:

- ABC share sum is approximately 100%;
- `cumulative_share` does not decrease;
- no negative sales;
- no negative stock;
- no division-by-zero coverage result;
- input SKU count equals output SKU count;
- `mock_mode=true` is explicit on reports/items.

## API endpoints

- `GET /analytics/abc`
- `GET /analytics/abc/{metric}`
- `GET /analytics/forecast`
- `GET /analytics/forecast/{sku}`
- `GET /analytics/stock-forecast`

## Telegram commands

- `/abc`
- `/abc revenue`
- `/abc profit`
- `/abc sales_qty`
- `/forecast`
- `/forecast_sku <sku>`

## Safety

All providers are mock providers. No real Wildberries, Ozon, Yandex Market, Telegram or LLM API is called by this module.
