# Data Contracts

Zentory agents must work with one internal marketplace data format. Wildberries, Ozon, Yandex Market, manual imports and mock fixtures should be normalized before they reach business logic.

## Source labels

`DataSourceLabel` is the shared source marker:

- `MOCK`
- `WB`
- `OZON`
- `YANDEX_MARKET`
- `MANUAL`

Mock data must always use `source=MOCK`. If mock and real sources are combined in one normalized SKU payload, the normalization layer must return a warning.

## Core entities

### MarketplaceAccount

Account-level identity for a seller account:

- `account_id`
- `marketplace`
- `seller_name`
- `legal_name`
- `is_active`
- `metadata`
- `source`
- `mock`

### SKUIdentity

Product identity shared by all agents:

- `sku`
- `nm_id`
- `vendor_code`
- `marketplace`
- `product_name`
- `category`
- `brand`
- `source`
- `mock`

### SalesSnapshot

Period sales snapshot:

- `date_from`
- `date_to`
- `orders_qty`
- `sales_qty`
- `revenue`
- `buyout_percent`
- `returns_qty`
- `avg_price`
- `source`
- `mock`

### StockSnapshot

Stock state aggregated across warehouses and regions:

- `total_stock`
- `stock_by_warehouse`
- `stock_by_region`
- `days_of_coverage`
- `out_of_stock`
- `source`
- `mock`

### AdsSnapshot

Advertising performance snapshot:

- `impressions`
- `clicks`
- `ctr`
- `spend`
- `orders`
- `revenue`
- `drr`
- `cpm`
- `cpc`
- `campaign_id`
- `source`
- `mock`

### ReviewSnapshot

Review and rating state:

- `rating`
- `reviews_count`
- `negative_reviews_count`
- `unanswered_reviews_count`
- `latest_reviews`
- `date_from`
- `date_to`
- `source`
- `mock`

### UnitEconomicsSnapshot

Unit economics for one SKU:

- `price`
- `cost`
- `commission`
- `logistics`
- `acquiring`
- `ads_cost`
- `tax`
- `storage`
- `return_logistics`
- `profit`
- `margin_percent`
- `source`
- `mock`

## Normalization service

`DataNormalizationService` is the boundary between external payloads and agent logic. Its role is to:

1. convert marketplace-specific fields into internal schemas;
2. preserve source labels;
3. keep mock data explicitly marked as `MOCK`;
4. warn when mock and real data are mixed;
5. return a `NormalizedSKUData` bundle for downstream agents.

Future WB/Ozon/Yandex adapters should call the normalization service before passing data to forecast, ads, promo, SKU intelligence or inventory agents.
