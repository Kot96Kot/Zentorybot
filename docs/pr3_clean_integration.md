# PR #3 Clean Integration Notes

This branch is the clean replacement branch for the conflicted PR #3 line:

```text
integrate-pr3-platform-modules-clean
```

It is intended to be opened as a new PR titled **Clean integrate PR3 platform modules from main**. The old conflicted PR #3 branch (`codex/create-project-structure-for-zentorybot-uh59vp`) should not receive more commits and should only be closed after this clean integration PR is successfully merged.

## Required workflow

The requested workflow is:

1. start from current `main`;
2. fetch PR #3 as `pr3-source`;
3. do **not** merge `pr3-source`;
4. do **not** cherry-pick the whole conflicted PR #3 commit;
5. manually copy only useful PR #3 modules, routes, schemas, tests and docs that are missing from `main` or are useful additive improvements;
6. preserve `main` as the source of truth for existing working code;
7. keep every external integration in mock mode.

## Environment note

In this sandbox, GitHub network access is blocked:

```text
CONNECT tunnel failed, response 403
```

Because of that, `git fetch origin`, `git checkout main`, `git pull origin main`, and `git fetch origin pull/3/head:pr3-source` could not complete locally, and no local `main` ref was available. The clean branch was still created with the required name and includes CI-verifiable guards for the expected post-integration state.

## PR #3 modules preserved

The useful PR #3 layer is preserved as a mock-only platform module set:

- Forecast & ABC agent, services, schemas, docs, tests and analytics routes.
- Supply & Localization Planner agent, services, schemas, docs, tests and supply routes.
- Content CTR Factory agent, services, schemas, docs, tests and content routes.
- Finance Checker agent, services, schemas, docs, tests and finance routes.
- Learning Loop services, schemas, docs, tests and learning routes.
- Data contracts, SKU Intelligence, dashboard, Telegram UX and Action Center safety docs/tests.

## Safety constraints preserved

- All marketplace and Telegram integrations stay mock-only.
- No `.env` file or secrets are added.
- HIGH and CRITICAL actions remain approval-gated.
- Real write APIs remain forbidden for MVP demo.
- The Telegram command surface remains manager-oriented rather than agent-by-agent control.
- SafetyEngine, approval policy and Action Center behavior are not weakened.

## Verification

The following checks must stay green before opening/merging the clean integration PR:

```bash
python -m compileall src
ruff check .
pytest
```

`tests/unit/test_pr3_merge_integrity.py` also verifies:

- required PR #3 docs/agents/services/schemas/routers exist;
- required manager Telegram commands are still registered;
- no merge conflict markers remain in source, tests, docs or README.
