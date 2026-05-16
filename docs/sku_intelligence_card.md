# SKU Intelligence Card

SKU Intelligence Card is a single management view for one marketplace product. It is designed so Telegram `/sku <sku>`, dashboard `/dashboard/sku/{sku}`, agents, and future real adapters can share the same structure.

## Goal

For one SKU, Zentorybot should show the full management picture:

- SKU and marketplace articles for Wildberries, Ozon, and Yandex Market;
- product name;
- sales for day, week, and month;
- revenue and margin;
- stock and coverage days;
- ad metrics: DRR, CTR, clicks, carts, orders, cart conversion, order conversion;
- rating and reviews;
- search position;
- competitor for comparison;
- strengths and weaknesses;
- recommendations and risks;
- actions that can be approved by a human.

## Mock-first structure

The current implementation uses `SKUIntelligenceService` with deterministic mock data. The schema is intentionally explicit and nested so each block can later be filled by real marketplace APIs without changing the UI contract.

## Entry points

- Telegram: `/sku <sku>` is parsed into the `sku_overview` event and handled by `SKUAgent`.
- Dashboard: `/dashboard/sku/{sku}` renders the same SKU intelligence card in Jinja2.
- Agent: `SKUAgent` returns an action payload with `sku_intelligence` and a short `telegram_response`.

## Safety

No real API is called. The SKU card only proposes mock approval actions and does not change prices, bids, cards, stock, or campaigns.
