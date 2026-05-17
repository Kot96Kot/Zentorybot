# Next steps

## 1. Preserve MVP demo stability

- Keep `ruff check .`, `pytest`, and `python -m compileall src` green.
- Keep `tests/unit/test_mvp_demo_readiness.py` aligned with demo endpoints and Telegram commands.
- Do not add real API calls to existing mock clients without a separate integration plan and safety review.

## 2. Prepare read-only WB API connection

Recommended first real integration target: **Wildberries read-only data**.

Order of connection:

1. Stocks.
2. Orders/sales.
3. Prices as read-only inputs.
4. Reviews/questions as read-only inputs.
5. Ads stats as read-only inputs.
6. Promo terms as read-only inputs.

Rules for this stage:

- Use `.env.example` names as reference only; do not commit `.env` or real tokens.
- Add marketplace-specific rate limits and retries before any production call.
- Normalize data through `DataNormalizationService` before passing it to agents.
- Keep all write actions disabled.
- Keep demo mock fixtures available for offline tests.

## 3. Move in-memory state to persistence

- Action Registry / Action Center storage.
- Audit log append-only storage.
- Idempotency keys table.
- Learning Loop action-result history.
- Telegram command/event history.

## 4. Connect real Telegram Bot API later

- Webhook secret validation.
- Real `sendMessage` implementation.
- Inline keyboards for approve/reject.
- User/tenant mapping.
- Role-based command permissions.

## 5. Connect real LLM provider later

- Keep `MockContentLLMProvider` as fallback.
- Add provider interface for external LLMs.
- Version prompts and store prompt/output audit.
- Add moderation/marketplace policy guardrails for generated content.

## 6. Write-actions activation plan

Do not enable write-actions during MVP demo. Future activation should be staged:

1. Draft/recommendations only.
2. Assisted mode with manual copy to marketplace UI.
3. Semi-auto with explicit HARD_APPROVAL and persistent audit/idempotency.
4. Controlled auto only for proven low-risk actions with strict limits and kill switch.

## 7. Production hardening

- Auth, tenants, roles.
- Secrets manager.
- Rate limiting and marketplace quotas.
- Monitoring, traces, alerts.
- Backup/restore.
- Sandbox/contract tests for marketplace adapters.

## 8. MVP demo gate checklist

Before demo:

1. Run `ruff check .`.
2. Run `pytest`.
3. Run `python -m compileall src`.
4. Start `make dev` in a dependency-complete environment.
5. Smoke-check the required API endpoints.
6. Smoke-check the required Telegram commands.
7. Keep all real APIs disabled.
8. Use `docs/mvp_demo_checklist.md` as the demo operator checklist.
