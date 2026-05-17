# Finance Checker

Finance Checker is a mock-only financial control module. It finds calculation mistakes, reconciles financial data and highlights SKU anomalies. It never makes payments and never edits final reports automatically.

## SKU profit formula

```text
SKU profit = revenue
  - commission
  - logistics
  - acquiring
  - advertising
  - cost
  - storage
  - penalties
  - return logistics
  - taxes
```

## Checks

The module detects:

- negative margin;
- price below minimum price;
- advertising consumed profit;
- missing commission;
- missing logistics;
- expenses greater than revenue;
- mismatch between marketplace report and internal table;
- suspicious expense spike;
- SKU without cost;
- missing taxes;
- DDS/cash-flow mismatch.

## Output issue contract

Each issue contains:

- `status`: `ok`, `warning`, `critical`;
- `issue_type`;
- `affected_sku`;
- `expected_value`;
- `actual_value`;
- `difference`;
- `recommendation`;
- `needs_human_check`.

## API endpoints

- `GET /finance/check`
- `GET /finance/pnl`
- `GET /finance/unit/{sku}`

## Telegram commands

- `/finance_check`
- `/pnl_check`
- `/unit <sku>`

## Safety

- No payments are made.
- Final reports are not changed automatically.
- The module only checks, highlights anomalies and recommends next actions.
- All data is deterministic mock data.
