# Action Center

Action Center is the single mock-only approval center for actions proposed by Zentorybot AI agents.

## Goal

Every agent action should be visible to a human before execution. The human can see:

- what the agent proposes;
- why it proposes it;
- risk and approval mode;
- evidence and data used;
- before/after state;
- what will change;
- whether rollback is available;
- approve/reject commands.

## Action fields

Each Action Center record contains:

- `action_id`
- `created_at`
- `agent_name`
- `action_type`
- `title`
- `description`
- `before_state`
- `after_state`
- `payload`
- `risk_level`
- `approval_mode`
- `status`
- `rollback_available`
- `explanation`
- `evidence`

## Statuses

- `proposed`
- `approved`
- `rejected`
- `executed`
- `failed`
- `rolled_back`

## Methods

`ActionCenter` exposes the MVP lifecycle:

- `create_action`
- `preview_action`
- `approve_action`
- `reject_action`
- `execute_action`
- `rollback_action`
- `list_pending_actions`
- `list_recent_actions`

## Mock execution only

`ActionExecutor` never calls real marketplace APIs. Execution only changes the in-memory action status and records audit metadata with `mock: true` and `external_api_called: false`.

This means Action Center can be used safely for UX, Telegram, dashboard, and approval-flow development without changing real prices, bids, cards, inventory, or campaigns.

## HTTP API

The Action Center is exposed through mock-safe REST endpoints for dashboard and integration tests:

- `POST /actions` creates a persisted action card.
- `GET /actions` lists recent cards newest-first.
- `GET /actions/pending` lists proposed and approved cards still requiring attention.
- `GET /actions/{action_id}` fetches one card.
- `GET /actions/{action_id}/preview` renders the explanation, evidence, changed fields and approve/reject buttons.
- `POST /actions/{action_id}/approve` and `POST /actions/{action_id}/reject` record the owner decision.
- `POST /actions/{action_id}/execute` performs a mock execution only when approval requirements are satisfied.
- `POST /actions/{action_id}/rollback` performs a mock rollback only for rollback-capable cards.

The legacy `POST /actions/preview` and `POST /actions/approve` routes remain available for orchestrator proposals stored in `ActionRegistry`.

