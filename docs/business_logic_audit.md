# Business Logic Audit: marketplace safety guards

This audit covers the current mock-only Zentorybot MVP business rules before any real marketplace APIs are connected. The related regression tests live in `tests/unit/test_business_logic_*.py`.

## Summary

- Total business rules audited: **33**.
- Rules covered by executable tests: **33**.
- Rules currently implemented and expected to pass: **21**.
- Rules documented as known gaps with strict `xfail` tests: **12**.
- Real API readiness: **not ready** for write operations that change prices, bids, campaign state, promo participation, content publication, feedback replies, or high-risk Action Center execution.

## Rule-by-rule status

| Area | Rule | Current status | Test coverage |
| --- | --- | --- | --- |
| Pricing | Price change that makes margin lower than the minimum must be blocked. | **Missing.** Price safety evaluates percentage only and ignores `new_margin_percent` / `minimum_margin_percent`. | `test_price_change_below_minimum_margin_is_blocked` (`xfail`) |
| Pricing | Price change above 5% requires approval. | **Implemented.** `SafetyRules._price_change` escalates to soft approval above 5%. | `test_price_change_above_5_percent_requires_approval` |
| Pricing | Price change above 15% requires hard approval. | **Missing.** The current rule treats 6% and 16% the same: medium + soft approval. | `test_price_change_above_15_percent_requires_hard_approval` (`xfail`) |
| Pricing | Price below себестоимость + mandatory expenses must be CRITICAL. | **Missing.** Price safety does not inspect cost or mandatory expenses. | `test_price_below_cost_plus_mandatory_expenses_is_critical` (`xfail`) |
| Ads | Bid increase is forbidden when stock is below 7 days. | **Implemented.** `ad_bid_increase` becomes CRITICAL, hard approval and blocked when `stock_days < 7`. | `test_bid_increase_is_blocked_when_stock_is_less_than_7_days` |
| Ads | DRR above limit creates warning or critical. | **Implemented in analysis reports.** High DRR creates warning/critical recommendations. | `test_drr_above_limit_creates_warning_or_critical` |
| Ads | Campaign with spend and no orders proposes pause but does not execute pause without approval. | **Implemented as recommendation.** Pause recommendation requires approval and is not auto-executable. | `test_spend_without_orders_proposes_pause_but_requires_approval` |
| Ads | Bid increase above 10% requires approval. | **Implemented.** `ad_bid_increase` above 10% requires soft approval. | `test_bid_increase_above_10_percent_requires_approval` |
| Inventory | Stock below 7 days is critical. | **Implemented.** Inventory status and priority become critical. | `test_stock_less_than_7_days_is_critical` |
| Inventory | Stock below 14 days is warning. | **Implemented.** Inventory status becomes warning and priority high. | `test_stock_less_than_14_days_is_warning` |
| Inventory | Out-of-stock increases task priority. | **Implemented.** Zero/near-zero coverage produces critical priority recommendations. | `test_out_of_stock_raises_task_priority` |
| Inventory | Advertised SKU with low stock alerts AdsAgent. | **Implemented.** Inventory report includes `alerts_for_ads_agent`. | `test_advertised_sku_with_low_stock_alerts_ads_agent` |
| Promo | Promo below minimum margin is forbidden. | **Implemented.** Promo analysis rejects margin-killing promotions. | `test_promo_below_minimum_margin_is_rejected` |
| Promo | Promo below себестоимость + expenses is CRITICAL. | **Implemented.** Promo price below mandatory costs is critical and rejected. | `test_promo_below_cost_plus_expenses_is_critical` |
| Promo | Slow mover promo can be allowed only through approval. | **Implemented.** Slow mover low-margin case can be `ALLOW_WITH_APPROVAL` and HIGH risk. | `test_slow_mover_promo_requires_approval` |
| Promo | Mass SKU participation in promo requires hard approval. | **Missing.** Promo safety does not inspect bulk `sku_count`. | `test_mass_promo_participation_requires_hard_approval` (`xfail`) |
| Content | Content cannot be published automatically. | **Missing in safety policy.** Generic content publish actions can remain low risk with no approval. | `test_content_cannot_be_published_automatically` (`xfail`) |
| Content | Card changes must go to draft. | **Implemented for generation.** Content generation returns draft status and requires approval. | `test_generated_card_changes_are_draft_and_require_approval` |
| Content | Card publication requires approval. | **Missing as explicit policy.** No dedicated publication approval rule exists. | `test_card_publication_requires_approval` (`xfail`) |
| Content | Mass content change requires hard approval. | **Missing.** Bulk content updates are not escalated by SKU count or field count. | `test_mass_content_change_requires_hard_approval` (`xfail`) |
| Feedback | Typical question can receive draft. | **Implemented as mock draft.** FeedbackAgent proposes `feedback_reply_draft`. | `test_typical_question_can_create_draft` |
| Feedback | Negative review requires approval. | **Missing.** FeedbackAgent does not classify rating/sentiment into approval mode. | `test_negative_review_requires_approval` (`xfail`) |
| Feedback | Complaint, warranty, return or legal risk requires hard approval. | **Missing.** No risk-tag escalation exists. | `test_complaint_warranty_return_or_legal_risk_requires_hard_approval` (`xfail`) |
| Feedback | Bot must not promise facts missing from knowledge base. | **Missing.** There is no knowledge-base grounding guard for replies. | `test_bot_does_not_promise_facts_missing_from_knowledge_base` (`xfail`) |
| Sales plan | Sales plan considers stock. | **Implemented.** Reports calculate `stock_days_left` and stock alerts. | `test_sales_plan_uses_inventory_for_stock_days` |
| Sales plan | Sales plan considers average sales speed. | **Implemented.** Day plan uses historical 7/14/30-day sales velocity. | `test_sales_plan_uses_average_sales_speed_for_day_plan` |
| Sales plan | Unreachable plan due to stock creates warning. | **Implemented.** Low stock creates alerts while bad plan status becomes warning/critical. | `test_unreachable_plan_due_to_stock_creates_warning` |
| Sales plan | Unreachable plan due to ads or conversion creates action recommendation. | **Partially implemented.** The service creates tasks/recommendations, but they are text-only and not Action Center actions. | `test_unreachable_plan_due_to_ads_or_conversion_creates_action_recommendation` |
| Action Center | Action cannot execute twice. | **Missing.** ActionCenter execution is not idempotent. | `test_action_cannot_execute_twice` (`xfail`) |
| Action Center | Rejected action cannot execute. | **Implemented.** Rejected actions remain rejected. | `test_rejected_action_cannot_execute` |
| Action Center | Executed action can roll back only when `rollback_available=true`. | **Implemented.** Rollback unavailable leaves status unchanged. | `test_executed_action_rolls_back_only_when_rollback_is_available` |
| Action Center | Every action has audit log. | **Implemented for create/approve/reject/execute/rollback flows.** Creation is covered directly. | `test_action_creation_has_audit_log` |
| Action Center | HIGH and CRITICAL cannot execute without hard approval. | **Missing.** ActionCenter trusts caller-provided `approval_mode`; HIGH + `NONE` can execute. | `test_high_and_critical_actions_cannot_execute_without_hard_approval` (`xfail`) |

## Dangerous-action risks found

1. **Pricing writes are unsafe for real APIs.** Price changes do not check minimum margin, cost price or mandatory expenses, and >15% changes do not force hard approval.
2. **Content writes are unsafe for real APIs.** Generated content is draft-safe, but safety rules do not block direct `content_publish`, `content_card_publish` or `content_bulk_update` actions.
3. **Feedback replies are unsafe for real APIs.** Negative/legal/warranty/return cases are not classified, and replies are not grounded against a knowledge base.
4. **Bulk promo writes are unsafe for real APIs.** Single-SKU promo economics are checked, but bulk participation does not force hard approval.
5. **Action Center execution is unsafe for real APIs.** The current `ActionCenter` can execute the same action repeatedly and can execute caller-misclassified HIGH/CRITICAL actions if `approval_mode=NONE`.
6. **Sales-plan recommendations are not actionable safety objects.** Ads/conversion issues are emitted as text tasks/recommendations, not guarded Action Center proposals.

## Rules already implemented

- Percentage threshold approval for price changes above 5%.
- Bid-increase stock guard and bid-increase approval threshold.
- DRR/spend/no-order ad warnings and pause recommendations.
- Inventory critical/warning thresholds, OOS priority and AdsAgent low-stock alerts.
- Single-SKU promo margin, mandatory-cost and slow-mover approval checks.
- Content generation as draft with approval required.
- Typical feedback question draft action.
- Sales-plan stock-days, historical sales velocity and low-stock alerts.
- Basic Action Center audit, rejection blocking and rollback availability guard.

## Rules absent or incomplete

- Pricing margin/cost gates and hard approval for >15% price changes.
- Content-specific safety policy for publish and bulk edits.
- Feedback-specific classifier and knowledge-base grounding.
- Bulk promo approval policy.
- Action Center idempotency and risk/approval consistency validation.
- Conversion/ad underperformance recommendations should become guarded action proposals, not only strings.

## Must fix before connecting real APIs

1. Add a price economics guard that validates new price against cost, mandatory expenses and minimum margin before any marketplace price update.
2. Add hard approval escalation for price changes above 15%.
3. Add content safety rules: all card mutations stay draft; publish requires approval; bulk changes require hard approval.
4. Add feedback safety rules: negative reviews require approval; complaint/warranty/return/legal cases require hard approval; replies must be grounded in approved knowledge-base facts.
5. Add bulk promo guard by SKU count / revenue impact / margin impact.
6. Make Action Center execution idempotent and block any HIGH/CRITICAL action unless `approval_mode=HARD_APPROVAL` and status is approved.
7. Convert sales-plan ad/conversion recommendations into Action Center proposals with risk, approval mode, evidence and audit trail.

## MVP demo gate update (2026-05-16)

The business-rule tests are suitable as an MVP demo safety gate because they make implemented safeguards and missing safeguards explicit. The 12 strict `xfail` tests are intentional documentation of gaps and must not be interpreted as permission to connect real APIs.

For demo: keep all actions mock-only.
For production/read-write integrations: convert every strict `xfail` in `tests/unit/test_business_logic_*.py` into a passing test before enabling the corresponding real API capability.
