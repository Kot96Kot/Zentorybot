# Supply & Localization Planner

Supply & Localization Planner is a mock-only module for warehouse stock risks, replenishment and regional localization decisions. It does not call marketplace, logistics or warehouse APIs.

## Input contract

Each row contains:

- `sku`
- `warehouse`
- `region`
- `stock_qty`
- `sales_qty_7d`
- `sales_qty_30d`
- `avg_daily_sales`
- `lead_time_days`
- `target_coverage_days`
- `localization_index`
- `logistics_cost`
- `available_for_supply`

Optional mock fields mark advertising and 3-period sales trend: `is_advertised`, `sales_qty_prev_30d`, `sales_qty_prev_prev_30d`.

## Output contract

Each recommendation contains:

- `recommended_supply_qty`
- `target_warehouse`
- `priority`
- `reason`
- `expected_coverage_days`
- `localization_impact`
- `replenishment_cost`
- `warning_list`

## Rules

- If stock coverage is less than 7 days, priority is `CRITICAL`.
- If stock coverage is less than 14 days, priority is `HIGH`.
- If SKU is advertised and stock is low, the report creates an alert for `AdsAgent`.
- If a warehouse has weak localization, the planner suggests redistribution to a better target warehouse.
- Slow movers do not receive extra supply without approval.
- If sales grow for three periods in a row, shipment priority is raised by one level.

## API endpoints

- `GET /supply/risks`
- `GET /supply/replenishment`
- `GET /supply/warehouses`
- `GET /supply/sku/{sku}`

## Telegram commands

- `/stock_risks`
- `/replenishment`
- `/warehouses`

## Safety

All data is deterministic mock data. The planner only proposes actions and never creates real supply orders or marketplace changes.
