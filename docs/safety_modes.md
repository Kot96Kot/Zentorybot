# Safety Modes

Zentory supports staged automation modes. The current MVP treats only **SHADOW** and **ASSISTANT** as working modes.

## SHADOW

The platform observes data and produces internal analysis without proposing executable changes to the marketplace.

- Status now: **working**.
- External writes: disabled.
- Human role: reviews reports and compares platform output with manual decisions.
- Best for: integration validation, formula validation, baseline data quality checks.

## ASSISTANT

The platform explains deviations and proposes actions, but a human owner must decide what to do.

- Status now: **working**.
- External writes: disabled in MVP; proposed actions remain mock-only.
- Human role: approves, rejects or manually applies recommendations.
- Best for: daily management, alerts, planning, stock and promo review.

## SEMI_AUTO

The platform can execute approved low-risk or medium-risk actions after explicit confirmation and safety checks.

- Status now: **not active**.
- External writes: not allowed in current MVP.
- Required before activation: real API adapter contracts, idempotency, audit persistence, rollback strategy and production safety review.

## AUTO

The platform executes selected low-risk recurring actions without per-action approval, while preserving limits, audit and rollback.

- Status now: **not active**.
- External writes: not allowed in current MVP.
- Required before activation: stable historical performance, measurable outcomes, strict limits, anomaly detection and emergency stop.

## Current operating rule

Until real integrations and safety contracts are complete, Zentory must operate only in **SHADOW** or **ASSISTANT** mode.
