# SKU Intelligence Card

SKU Intelligence Card is the shared mock contract for a single SKU management view. The same structure is used by:

- API: `GET /sku/{sku}/intelligence`;
- Telegram: `/sku <sku>` parsed as `sku_overview` and handled by `SKUAgent`;
- Dashboard: `/dashboard/sku/{sku}`;
- future marketplace adapters that will replace mock data without changing the card contract.

## Contract

The card is intentionally explicit and grouped by business block.

### 1. Basic

- `sku`
- `nm_id`
- `vendor_code`
- `marketplace`
- `product_name`
- `category`
- `brand`

### 2. Sales

- `sales_qty_day`
- `sales_qty_7d`
- `sales_qty_30d`
- `revenue_day`
- `revenue_30d`
- `avg_price`
- `buyout_percent`

### 3. Stock

- `total_stock`
- `stock_by_warehouse`
- `days_of_coverage`
- `stock_status`

### 4. Advertising

- `impressions`
- `ctr`
- `clicks`
- `spend`
- `drr`
- `orders_from_ads`
- `campaign_status`

### 5. Conversion

- `cart_conversion`
- `order_conversion`
- `click_to_order`

### 6. Reputation

- `rating`
- `reviews_count`
- `negative_reviews_count`
- `unanswered_questions`

### 7. Competitors

- `competitor_sku`
- `competitor_price`
- `competitor_rating`
- `where_we_are_stronger`
- `where_we_are_weaker`

### 8. Risks

- `low_stock`
- `high_drr`
- `low_ctr`
- `low_margin`
- `rating_risk`
- `out_of_stock`

### 9. Recommendations

Each recommendation contains:

- `title`
- `reason`
- `expected_effect`
- `risk_level`
- `approval_required`

## Current behavior

`SKUIntelligenceService` returns deterministic mock data only. No Wildberries, Ozon, Yandex Market, Telegram, or LLM API calls are made.

`SKUAgent` wraps the same card into an action payload:

- `payload.sku_intelligence` contains the full card;
- `payload.telegram_response` contains a short manager-facing summary with problem, reason, recommendation, risk, and approval requirement.

## Safety

The SKU card is read-only in the MVP. Recommendations may mark `approval_required=true`, but they do not execute real marketplace changes.
