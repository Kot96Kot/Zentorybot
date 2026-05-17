# Web Dashboard

Zentorybot includes a simple FastAPI + Jinja2 dashboard for visualizing how mock AI agents work. It is intentionally not a React app: the goal is a lightweight management panel for local MVP inspection.

## Pages

| Page | Purpose |
| --- | --- |
| `/dashboard` | Overview: system status, safety mode, alert count, approval count, risky SKU, recent agent actions, agent health. |
| `/dashboard/alerts` | Mock alerts that require manager attention. |
| `/dashboard/actions` | Proposed actions, approval mode, risk, and status. |
| `/dashboard/sku/{sku}` | SKU Intelligence Card with articles, sales, revenue, margin, stock, ads, reviews, competitor, risks, recommendations, and approval actions. |
| `/dashboard/agents` | Mock readiness and status of AI agents. |
| `/dashboard/audit` | Mock audit trail showing agent and Safety Core activity. |

## Design

The UI uses server-rendered HTML templates and a single CSS file:

- white background;
- card layout;
- simple tables;
- red for critical states;
- yellow for warning states;
- green for ok states;
- black/gray text.

## Mock-only guarantee

The dashboard uses in-memory mock data from `zentory.web.routes`. It does not connect to real Telegram, Wildberries, Ozon, Yandex Market, database, or LLM APIs. It does not change prices, bids, stock, cards, or campaigns.

## Local usage

Start the app:

```bash
make dev
```

Open:

```text
http://localhost:8000/dashboard
```

## MVP demo verification (2026-05-16)

The dashboard is ready for local MVP demo once dependencies are installed. It is intentionally server-rendered and mock-only. It should be used to demonstrate agent status, alerts, action cards, SKU intelligence and audit visibility, not to operate real marketplace accounts.
