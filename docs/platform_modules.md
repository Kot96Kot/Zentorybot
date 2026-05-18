# Platform Modules Clean Integration

This document describes the clean integration of platform modules that were requested from PR #3 without merging the conflicting branch.

## Modules

- **Forecast & ABC**: creates a 14-day mock demand forecast, assigns ABC classes, and highlights stockout risks.
- **Supply & Localization Planner**: proposes warehouse transfers and regional coverage improvements without creating real supplies.
- **Content CTR Factory**: drafts safe content experiments for CTR improvements and keeps publication behind approval.
- **Finance Checker**: validates contribution profit, gross margin, and DRR before discount or bid decisions.
- **Learning Loop**: records metric deltas and converts them into future rule updates.
- **Data Contracts**: defines stable mock contracts for SKU snapshots and action recommendations.
- **SKU Intelligence alignment**: the modules use the same mock SKU ids as the existing SKU Intelligence Card.

## API

All endpoints are read-only and mock-safe:

- `GET /platform/modules`
- `GET /platform/forecast-abc`
- `GET /platform/supply-localization`
- `GET /platform/content-ctr`
- `GET /platform/finance-checker`
- `GET /platform/learning-loop`
- `GET /platform/data-contracts`

## Safety

The integration does not call real marketplace APIs. Recommendations are advisory and any future write action must pass through Action Center, approval modes, and rollback metadata.
