# Full Code Audit

Audit date: 2026-05-16  
Scope: full repository static review plus requested command checks.  
Important constraint: no product code was changed during this audit; this file is the only intended audit artifact.

## Critical issues

| id | файл | проблема | риск | как исправить |
|---|---|---|---|---|
| C-01 | `src/zentory/actions/registry.py` | `execute_mock(..., force=True)` still evaluates safety but then bypasses `allowed_to_execute` and `SafeModeService.ensure_can_execute`. A HIGH/CRITICAL or blocked action can be executed in mock flow by passing `force=True`. | Safety Core can be bypassed; this violates the requirement that dangerous actions cannot execute without risk checks, limits, approval and audit. | Remove public force bypass or restrict it to hard-approved admin/test paths with explicit audit reason; never bypass `SafetyDecision.allowed_to_execute` for blocked/HIGH/CRITICAL actions. |
| C-02 | `src/zentory/actions/action_center.py`, `src/zentory/actions/action_executor.py` | Action Center execution does not call `SafetyEngine`, does not use idempotency, and can execute the same action repeatedly. Approval gating only checks `approval_mode`, not current risk/safety decision. | The intended single approval center can bypass the strongest safety/idempotency layer and produce inconsistent execution history. | Inject `SafetyEngine` and `IdempotencyStore` into Action Center/Executor; require approved safety decision before execution; block repeat execution unless explicitly idempotent. |
| C-03 | `src/zentory/api/routers/actions.py`, `src/zentory/api/routers/telegram.py`, `src/zentory/api/dependencies.py` | HTTP and Telegram approval flows use `ActionRegistry`; the new `ActionCenter` is not wired into API dependencies or endpoints. `/actions/preview` still calls Orchestrator directly instead of Action Center preview. | The newly created Action Center is effectively parallel/unintegrated; human approval UI and API can approve one store while Action Center holds another. | Add a cached `ActionCenter` dependency and route create/preview/approve/reject/execute/rollback/list flows through it; keep `ActionRegistry` as compatibility layer or migrate it. |
| C-04 | `src/zentory/db/base.py`, `src/zentory/db/models/*.py`, `migrations/versions/.gitkeep` | DB models have primary key `id` without default generation, no actual Alembic revision files, and dict payload fields rely on weak/incomplete JSON typing. | Persistence layer is likely unusable for inserts/migrations once production storage is enabled. | Add UUID defaults, explicit JSON/JSONB columns, tenant relationships, nullable decisions, and initial Alembic revision matching current models. |

## High issues

| id | файл | проблема | риск | как исправить |
|---|---|---|---|---|
| H-01 | Environment / `pyproject.toml` | `pytest` cannot collect tests in the current environment because `fastapi` and `pydantic` are missing. `python -m compileall src` passes because it does not import third-party modules deeply enough to validate runtime availability. | App startup and endpoint verification are blocked in this environment; claims that full pytest passes cannot be verified here. | Ensure `python -m pip install -e ".[dev]"` is run in CI/local validation; consider a lock file or `requirements-dev.txt` for reproducible setup. |
| H-02 | `src/zentory/decision/engine.py`, `src/zentory/decision/scoring.py`, `src/zentory/decision/safety_rules.py` | DecisionEngine primarily scores event risk and existing action risk. SafetyRules only recognize exact action types such as `price_change`, `ad_bid_increase`, `promo_participation`, and a few ad boost names. Many agent action types (`ads_recommendation_*`, `sales_plan_alert`, `content_analysis_task`) bypass domain safety rules. | Risk and approval can be under-classified for real workflows; dangerous action names that do not match exact strings can avoid limits. | Normalize action taxonomy; route all proposed actions through SafetyEngine; add type/category metadata and tests for all agent-produced action types. |
| H-03 | `src/zentory/actions/action_center.py` | `execute_action` returns unchanged `PROPOSED` for missing approval and unchanged `REJECTED` for rejected actions. The `failed` status exists but is not used for blocked execution. | Status lifecycle is ambiguous and dashboards/API cannot distinguish “not attempted” from “attempt blocked”. | Define a transition table; set `FAILED` only for attempted failures or add `BLOCKED`; audit every blocked transition consistently. |
| H-04 | `src/zentory/agents/orchestrator.py` | If no agent can handle an event, Orchestrator returns a successful `DecisionResult` with zero actions. If an agent raises, exceptions propagate except where Telegram catches broadly. | Silent no-op makes broken routing hard to detect; `/actions/preview` can fail with 500 on agent exceptions. | Add explicit “no_agent_found” result/audit event; catch per-agent exceptions and continue or return structured failure actions. |
| H-05 | `docs/telegram_control_center.md`, `docs/*_module.md`, `src/zentory/agents/team/*.py` | Docs and AI-team role metadata still reference old Telegram commands (`/sales_plan`, `/ads_today`, `/stock_risks`, `/content_new`, `/promo_check`, `/unit`, `/agents`, etc.) while the parser supports only the simplified command set. | User-facing docs contradict implementation and tests; operators will try commands that now route to help/unsupported flow. | Update legacy docs/team-role command metadata or clearly mark old commands as internal events, not Telegram commands. |
| H-06 | `src/zentory/integrations/*/client.py` | Marketplace clients expose write-like methods (`update_price`, `send_reply`) directly. They are mock and return `not_sent`, but they do not require Action Center/Safety/Audit. | Future real adapter work could accidentally wire direct writes and bypass safety. | Move write-like adapter methods behind ActionExecutor interfaces; add comments/tests that direct write methods remain private/mock-only. |
| H-07 | `src/zentory/web/routes.py`, `src/zentory/web/templates/actions.html` | Dashboard action list is hardcoded mock data and not connected to ActionCenter/ActionRepository. | Dashboard can show actions that are not approvable and miss real proposed actions from Orchestrator. | Inject/use ActionCenter repository for dashboard actions; keep mock seed data only as fallback. |
| H-08 | `src/zentory/actions/action_repository.py` | In-memory repository has no locking or transaction boundary. Status changes mutate object references directly. | Concurrent API requests can double-execute or observe inconsistent status. | Add idempotency, immutable event log, or DB-backed transaction semantics before production use. |

## Medium issues

| id | файл | проблема | риск | как исправить |
|---|---|---|---|---|
| M-01 | `src/zentory/actions/schemas.py`, `src/zentory/schemas/actions.py` | There are two action schema models (`Action` and `ActionRecord`) with overlapping but different meanings. | Schema drift and confusion between ActionRegistry and ActionCenter. | Define one canonical action DTO or explicit conversion layer with tests. |
| M-02 | `src/zentory/agents/__init__.py` | Importing any submodule under `zentory.agents` triggers all agent imports via package `__init__`. This increases import surface and makes missing optional dependencies fail earlier. | Tests/imports fail broadly when one agent dependency breaks; cycle risk grows. | Use lazy exports or import concrete agents directly in Orchestrator without package-wide eager imports. |
| M-03 | `src/zentory/integrations/telegram/formatter.py` | Formatting is mostly string/dict based; button payloads are untyped and mypy reports generator item type issues. | Formatting can break at runtime if `buttons` contain malformed dictionaries. | Add Pydantic/dataclass message/card models and stricter button normalization. |
| M-04 | `src/zentory/agents/orchestrator.py` | Orchestrator still contains hardcoded Telegram UX business cards for `/daily`, `/alerts`, `/plan`, while SKU was moved to `SKUAgent`. | Business logic is split between Orchestrator and agents, causing duplication and uneven routing. | Move daily/alerts/plan card builders into dedicated agents/services. |
| M-05 | `src/zentory/services/rollback_service.py`, `src/zentory/actions/action_center.py` | There are two rollback mechanisms: RollbackService plans and ActionCenter rollback flag/executor. They are not connected. | `/rollback` may report unavailable even when ActionCenter says rollback is available. | Unify rollback source of truth or have ActionCenter create RollbackService plans. |
| M-06 | `src/zentory/services/safe_mode.py`, `src/zentory/decision/approval_modes.py` | SafeModeService and SafetyEngine modes are separate concepts with no central configuration. ActionRegistry creates SafetyEngine in AUTO while SafeModeService defaults enabled. | Runtime behavior is confusing: AUTO says allowed within limits but SafeMode still blocks unless forced. | Add a single settings-backed safety mode and document the relationship. |
| M-07 | `src/zentory/services/sku_intelligence_service.py` | SKU intelligence uses deterministic mock values for every SKU; dashboard top-risk cards call service repeatedly and all SKUs share identical metrics except SKU/article. | Mock UX can mislead tests/users into believing SKU-specific analysis exists. | Add a fixture map keyed by SKU and clear “mock fixture” labels in UI. |
| M-08 | `src/zentory/db/session.py` | Engine is created at import time using settings. | Importing DB session can try to configure production DB too early and complicate tests. | Lazy-create engine/session factory or inject settings. |
| M-09 | `migrations/env.py` | Alembic imports app settings and uses current `DATABASE_URL` even when no revisions exist. | Migration command may point at wrong DB and still have no schema version to apply. | Add generated revision and safer env handling. |
| M-10 | `tests/unit/test_action_center.py` | Tests check returned object references after later mutation in some flows indirectly; mutable reference behavior can mask lifecycle bugs. | Tests may pass even if status mutation order is wrong. | Re-fetch records after each transition and assert distinct lifecycle states. |
| M-11 | `src/zentory/api/routers/telegram.py` | Unknown commands are parsed to `control_help` with `error="unsupported_command"`, but webhook does not explicitly surface unsupported command status. | Users receive help but API response does not clearly say command was unsupported. | Handle `unsupported_command` similarly to `missing_argument`. |
| M-12 | `src/zentory/schemas/__init__.py` | `TeamRoleDefinition` is listed in `__all__` before its import occurs at the bottom. Runtime eventually works, but import order is surprising. | Increases maintenance confusion and mypy/import-order noise. | Move `team` imports with the rest and sort `__all__`. |

## Low issues

| id | файл | проблема | риск | как исправить |
|---|---|---|---|---|
| L-01 | `src/zentory/workers/*.py` | Worker modules are placeholders with only comments/empty implementation. | README suggests workers exist but they do nothing. | Mark as placeholders in README/docs or add minimal no-op functions/tests. |
| L-02 | `src/zentory/integrations/*/auth.py` | Three `MarketplaceAuth` dataclasses are duplicated per marketplace. | Minor duplication. | Move to shared integration auth module. |
| L-03 | `docs/mvp_status.md`, `docs/next_steps.md` | Documentation is broad and sometimes describes desired future state without clear “implemented vs planned” separation. | Reader confusion. | Add status badges/sections per capability. |
| L-04 | `src/zentory/web/static/styles.css` | CSS has long one-line rules that are readable but harder to diff. | Low maintainability. | Format CSS with a formatter if adopted. |
| L-05 | `src/zentory/services/reports_service.py` | Daily report is very small compared to dashboard/SKU intelligence data. | Report endpoint provides less value than docs imply. | Reuse SKU/report services to enrich report. |

## Broken logic

| id | область | проблема | риск | как исправить |
|---|---|---|---|---|
| BL-01 | Safety bypass | `ActionRegistry.execute_mock(force=True)` can bypass safety and safe mode. | Dangerous action lifecycle can be bypassed. | Remove/lock down force; require SafetyDecision + approval. |
| BL-02 | Action Center | No idempotency in ActionCenter; repeated `execute_action` can audit/execute repeatedly. | Duplicate side effects once real APIs are added. | Add idempotency key/state guard: executed actions must not execute again. |
| BL-03 | Approval | `ActionRegistry.approve` and ActionCenter approval do not validate that action exists in the same central store. | Split-brain approval state. | Use one repository for all action lifecycle. |
| BL-04 | Marketplace rules | Price/margin, low-stock ad boost, promo margin checks exist only for limited action types. | Agent-produced action types can avoid business safety rules. | Map every agent action to safety category. |
| BL-05 | Negative feedback | There is no explicit rule preventing automatic negative-review replies; clients expose `send_reply`. | Future direct integration could auto-reply. | Add feedback safety policy and tests. |
| BL-06 | Sales plan vs stock | Sales plan actions/tests do not prove stock constraints affect sales-plan recommendations. | Plans may ignore stock reality. | Inject inventory snapshot into SalesPlanService and add tests. |
| BL-07 | Mock/real separation | Many payloads have `mock: True`, but no global runtime enforcement prevents mixing mock data with future real data. | Reports could mix real and mock without visible marking. | Add data provenance fields and validation. |

## Architecture mismatches

| id | mismatch | details | recommendation |
|---|---|---|---|
| A-01 | ActionRegistry vs ActionCenter | Both manage action status, approval and execution; API/Telegram use ActionRegistry while new ActionCenter is not integrated. | Pick ActionCenter as lifecycle owner and make ActionRegistry an adapter or remove duplication later. |
| A-02 | Telegram docs vs parser | Parser supports the minimal command set, but older docs and AI team role metadata list removed commands. | Update docs and role metadata to minimal UX or mark old commands as internal events. |
| A-03 | Dashboard vs services | Dashboard actions/audit are hardcoded and not connected to ActionCenter/AuditService. SKU page uses service; actions page does not. | Connect dashboard pages to service/repository layer. |
| A-04 | Safety modes | SafetyEngine modes and SafeModeService are independent, and defaults conflict (`AUTO` plus safe mode enabled). | Centralize safety configuration. |
| A-05 | DB scaffold vs runtime | DB models and Alembic exist, but app services are in-memory and no migrations exist. | Document as scaffold only or implement persistence intentionally. |
| A-06 | Agent names | User-facing name `SkuAgent` differs from class `SKUAgent`; docs/tests should standardize casing. | Choose one naming convention. |

## Missing tests

| area | missing coverage |
|---|---|
| FastAPI startup | Cannot validate in current environment; add CI assertion for `create_app()` route list and lifespan. |
| Endpoints | Need tests for `/actions/preview` behavior when no agent found, `/actions/approve` not found, unknown Telegram command response, `/rollback` with existing rollback plan. |
| Safety Core | Need tests for force bypass prevention, all automation modes, all agent-produced action types, mass SKU hard approval, negative review reply blocking. |
| Action Center | Need idempotency/double-execute tests, SafetyEngine integration tests, ActionRegistry-to-ActionCenter migration tests. |
| Orchestrator | Need no-agent-found and failing-agent tests outside Telegram webhook. |
| Dashboard | Need tests that dashboard action page reflects ActionCenter repository once integrated; template smoke tests with empty data. |
| Integrations | Need tests proving write-like adapter methods are not reachable except through approved action execution. |
| DB | Need model metadata/migration tests, insert tests, tenant relationship tests. |
| Documentation | Need docs consistency checks for Telegram command list. |

## Security risks

| id | файл | риск | оценка | как исправить |
|---|---|---|---|---|
| S-01 | `src/zentory/actions/registry.py` | Force execution bypass can override safety/safe mode. | Critical | Remove or strongly guard `force`. |
| S-02 | `src/zentory/integrations/*/client.py` | Direct write-like methods are public. | High | Keep write operations behind ActionCenter/Safety layer. |
| S-03 | `src/zentory/api/routers/telegram.py` | No Telegram webhook secret validation. | Medium | Validate `TELEGRAM_WEBHOOK_SECRET` header/signature in non-local mode. |
| S-04 | `src/zentory/services/audit_service.py` | Audit is in-memory only and can be lost on process restart. | Medium | Persist audit logs before production. |
| S-05 | `.env.example` | No real secrets found; only placeholder variable names. | OK | Keep `.env` ignored and avoid committing secrets. |
| S-06 | repo-wide grep | No obvious hardcoded tokens/passwords/secret values found. | OK | Add secret scanning in CI. |

## Suggested fix order

1. Install dependencies in CI/local environment and make `pytest` executable end-to-end.
2. Remove or lock down `ActionRegistry.execute_mock(force=True)` safety bypass.
3. Integrate ActionCenter with ActionRegistry/API/Telegram/Dashboard or select one canonical action lifecycle.
4. Add SafetyEngine + IdempotencyStore to ActionCenter execution.
5. Normalize all agent action types to safety categories and add coverage for every agent-produced action.
6. Fix DB model defaults/types and add an initial Alembic revision.
7. Update legacy Telegram docs/team-role metadata to the simplified command set.
8. Move remaining hardcoded Orchestrator dashboard/Telegram business cards into services/agents.
9. Add webhook secret validation and persistent audit for non-local mode.
10. Add docs consistency tests and missing endpoint/negative-path tests.

## Commands executed

| command | result | notes |
|---|---|---|
| `git status --short` | Passed | Working tree was clean before audit file creation. |
| `python -m compileall src` | Passed | All source files compiled to bytecode. This does not validate missing third-party imports at runtime. |
| `pytest` | Failed | Collection interrupted with 17 errors. Root causes in this environment: `ModuleNotFoundError: No module named 'fastapi'` and `ModuleNotFoundError: No module named 'pydantic'`. 3 tests were collected before interruption. |
| `ruff check .` | Passed | All Ruff checks passed. |
| `mypy src` | Failed | `mypy` is available but not configured in `pyproject.toml`. It reported 45 errors, mostly missing third-party imports (`pydantic`, `fastapi`, `sqlalchemy`) plus real typing issues in `schemas/sales_plan.py`, `integrations/telegram/formatter.py`, and `agents/orchestrator.py`. |
| `rg -n "token|secret|api[_-]?key|password|Bearer|sk-|AKIA|BEGIN .*PRIVATE|print\\(" -S . ...` | Passed with findings | Found only placeholder/config field names; no hardcoded secret values. |
| `rg -n "/sales_plan|/ads_today|..." README.md docs src tests` | Passed with findings | Found stale old Telegram commands in docs and team-role metadata. |

## Endpoint audit notes

Because `fastapi` is not installed in the current container, endpoint runtime checks could not be executed. Static review shows routers are included in `create_app()` for health, telegram, actions, reports, and dashboard. Expected endpoints are declared:

- `GET /health` and `GET /ready` in `src/zentory/api/routers/health.py`.
- `POST /telegram/webhook` in `src/zentory/api/routers/telegram.py`.
- `POST /actions/preview` and `POST /actions/approve` in `src/zentory/api/routers/actions.py`.
- `GET /reports/daily` in `src/zentory/api/routers/reports.py`.

Main runtime blocker in this environment is missing installed dependencies, not a syntax error.

## Agent audit notes

All listed agents implement the `BaseAgent` interface with `analyze()` and `propose_actions()`. No agent directly calls real marketplace APIs. However, proposed actions are heterogeneous and do not all map cleanly to SafetyRules. The `SKUAgent` is integrated into Orchestrator for `sku_overview`, but the class name uses `SKUAgent` while the requested audit name says `SkuAgent`.

## Summary counts

- Critical issues: 4
- High issues: 8
- Medium issues: 12
- Low issues: 5
