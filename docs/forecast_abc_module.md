# Forecast & ABC Module

Forecast & ABC Agent is a mock-only analytics module for marketplace sellers. It prepares ABC classification, average daily sales and stock forecasts for 30, 60 and 90 days without changing prices, ads, cards or inventory.

## Data provider interface

The module uses a provider boundary named `MarketplaceSalesProvider`. Future Wildberries, Ozon and Yandex Market adapters should implement these methods:

- `fetch_sales_by_sku(date_from, date_to)`
- `fetch_orders_by_sku(date_from, date_to)`
- `fetch_stocks_by_warehouse()`
- `fetch_stock_movements()`
- `fetch_product_mapping()`

The current implementation uses `MockMarketplaceSalesProvider`. It returns explicit mock data: `sku`, `nm_id`, `vendor_code`, product name, warehouse, region, stock, 7/14/30-day sales, 30-day revenue, buyout percent, price, cost, ad spend and returns.

## Warehouse aggregation

Stock is collected by warehouse first. `ForecastService.load_aggregated_skus()` groups rows by `sku` and builds:

- `stock_by_warehouse` — warehouse-level stock dictionary;
- `total_stock` — total quantity across all warehouses;
- `stock_by_region` — region-level stock dictionary.

This keeps the MVP ready for real WB stock APIs where one SKU can appear on several warehouses.

## ABC analysis

ABC analysis can be calculated by `revenue`, `profit` or `sales_qty`.

Algorithm:

1. Sort SKU by selected metric descending.
2. Calculate total metric.
3. Calculate SKU share: `share = sku_metric / total_metric`.
4. Calculate cumulative share: previous shares plus current share.
5. Assign class:
   - `A`: cumulative share `<= 80%`;
   - `B`: cumulative share `> 80%` and `<= 95%`;
   - `C`: cumulative share `> 95%`.

Cumulative share shows how much of the total business metric is explained by the ranked SKU set up to the current row.

## Average daily sales

The service calculates:

- `avg_daily_sales_7d = sales_qty_7d / active_sales_days_7d`;
- `avg_daily_sales_14d = sales_qty_14d / active_sales_days_14d`;
- `avg_daily_sales_30d = sales_qty_30d / active_sales_days_30d`.

Out-of-stock days matter because dividing by calendar days understates demand when the item was unavailable. If active-stock days are missing, the module falls back to calendar days and adds the warning: `Расчет сделан без учета out-of-stock дней`.

## Stock forecast

The base formulas are:

- `base_forecast_sales_30 = avg_daily_sales * 30`;
- `base_forecast_sales_60 = avg_daily_sales * 60`;
- `base_forecast_sales_90 = avg_daily_sales * 90`.

The final forecast includes seasonality and trend:

```text
forecast_sales = avg_daily_sales * days * seasonality_coefficient * trend_coefficient
```

Coverage:

```text
stock_coverage_days = total_stock / avg_daily_sales
```

If `avg_daily_sales = 0`, coverage is `null` and status is `no_sales`.

Statuses:

- `ok`: stock covers more than 30 days;
- `warning`: stock covers from 14 to 30 days;
- `critical`: stock covers less than 14 days;
- `out_of_stock`: stock is zero.

## Seasonality and trend

`SeasonalityService` supports coefficients by category, month and SKU override. The mock config includes a cosmetics monthly matrix and SKU override for `ZNT-COS-001`.

Trend is calculated as:

```text
trend_coefficient = recent_avg_daily_sales / previous_avg_daily_sales
```

The result is limited to `0.7 <= trend_coefficient <= 1.5`.

## Self-check layer

All calculations pass through `CalculationSelfCheckService`. It checks:

- ABC shares sum to about 100%;
- cumulative share does not decrease;
- stock, sales, revenue, average daily sales and forecasts are non-negative;
- no division by zero when average daily sales is zero;
- zero total ABC metric produces a warning;
- input SKU count matches output SKU count;
- lost SKU mapping produces a warning;
- mock reports explicitly set `mock_mode=true`.

If critical errors are found, `ForecastService.full_report()` marks the recommendation as: `Расчет требует проверки человеком`.

## Telegram commands

The module supports mock Telegram commands:

- `/abc`
- `/abc revenue`
- `/abc profit`
- `/forecast`
- `/forecast_sku <sku>`
- `/stock_forecast`
- `/seasonality`

`/abc` returns SKU count, revenue context, class summaries, top SKU and self-check warnings. `/forecast_sku <sku>` returns stock, average daily sales, coverage, 30/60/90-day forecast, replenishment quantities, risks, seasonality, trend and self-check status.

## API endpoints

- `GET /analytics/abc`
- `GET /analytics/abc/{metric}`
- `GET /analytics/forecast`
- `GET /analytics/forecast/{sku}`
- `GET /analytics/stock-forecast`

All endpoints return JSON from mock data.

## What is mock now

- Sales and orders.
- Warehouse stocks.
- Stock movements.
- Product mapping.
- Seasonality coefficients.

No real WB/Ozon/Yandex Market APIs are called.

## What is needed for real WB API

1. Implement a Wildberries provider behind `MarketplaceSalesProvider`.
2. Map WB warehouse IDs to regions.
3. Load real sales, orders, stocks and product mappings in read-only shadow mode.
4. Persist snapshots and self-check results.
5. Compare mock and real calculations in CI/staging.
6. Keep the module read-only; any replenishment or campaign changes must go through Action Center and Safety Core.
