# Platform Algorithm

Zentory is an **AI operating system for marketplace operations**, not a command bot. Telegram, HTTP endpoints and dashboards are control surfaces; the core product is a closed operational loop that turns data into checked, approved and audited actions.

## Main loop

```text
Data → Analysis → Recommendation → Self-check → Approval → Action → Audit → Learning
```

1. **Data** — the platform reads marketplace, warehouse, advertising, financial and customer-feedback signals. In the current MVP these inputs are mock-only.
2. **Analysis** — agents find deviations, risks and opportunities: stockouts, margin drops, ad overspend, weak content, failed promo economics or forecast gaps.
3. **Recommendation** — each agent explains what happened, why it happened and which action should be considered.
4. **Self-check** — calculations and proposed decisions are checked before they can be shown as reliable recommendations.
5. **Approval** — the human owner approves, rejects or requests changes depending on safety mode, risk level and approval policy.
6. **Action** — approved actions are executed only through the Action layer. In the MVP this remains mock-only and must not call real marketplace APIs.
7. **Audit** — every recommendation, approval, rejection, execution and rollback is recorded with context and risk metadata.
8. **Learning** — the platform records effects after decisions so future recommendations can be compared against outcomes.

## Demo execution contract

- SHADOW and ASSISTANT are the only modes allowed for demo operations.
- HIGH and CRITICAL risks require HARD_APPROVAL and are not auto-executed.
- Real marketplace and Telegram write APIs are forbidden during MVP demo.
- Action execution is mock-only and must explicitly return mock markers.
- Learning Loop can record outcomes, but it cannot declare success without post-action metrics.

## Operational contour

The platform should behave as an operating contour:

1. Sees data.
2. Finds deviations.
3. Explains the cause.
4. Proposes an action.
5. Checks the calculation.
6. Requests confirmation.
7. Records the result.
8. Remembers the effect.

This loop is the baseline contract for all current and future agents.
