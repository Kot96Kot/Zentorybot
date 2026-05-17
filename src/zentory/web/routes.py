from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from zentory.services.sku_intelligence_service import SKUIntelligenceService

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _mock_dashboard_data() -> dict[str, Any]:
    alerts = [
        {
            "id": "alert-stock-wb-mock-1",
            "severity": "critical",
            "title": "WB-MOCK-1 закончится через 5 дней",
            "source": "InventoryAgent",
            "reason": "остаток ниже safety-порога 7 дней",
            "recommendation": "не усиливать рекламу и создать задачу на пополнение",
        },
        {
            "id": "alert-ads-acos-7",
            "severity": "warning",
            "title": "ADS-7 выше ACOS-лимита на 4 п.п.",
            "source": "AdsAgent",
            "reason": "ставка выросла быстрее продаж",
            "recommendation": "снизить ставку после approval",
        },
        {
            "id": "alert-review-size",
            "severity": "warning",
            "title": "Отзывы жалуются на размерную сетку",
            "source": "FeedbackAgent",
            "reason": "3 новых отзыва с одинаковым паттерном",
            "recommendation": "обновить блок размеров в карточке SKU",
        },
    ]
    actions = [
        {
            "action_id": "act-price-001",
            "title": "Снизить цену WB-MOCK-2 на 3%",
            "agent": "UnitEconomicsAgent",
            "risk": "LOW",
            "approval": "NONE",
            "status": "proposed",
        },
        {
            "action_id": "act-ads-007",
            "title": "Снизить ставку кампании ADS-7",
            "agent": "AdsAgent",
            "risk": "MEDIUM",
            "approval": "SOFT_APPROVAL",
            "status": "approval_required",
        },
        {
            "action_id": "act-promo-013",
            "title": "Отклонить акцию с маржой 12%",
            "agent": "PromoAgent",
            "risk": "CRITICAL",
            "approval": "HARD_APPROVAL",
            "status": "blocked_by_safety",
        },
    ]
    skus = SKUIntelligenceService().list_top_risky_skus() + [
        {
            "sku": "YM-MOCK-3",
            "name": "Товар Яндекс Маркет",
            "risk": "ok",
            "stock_days": 21,
            "sales_delta": "+4%",
            "ads": "в норме",
            "recommendation": "наблюдать",
        }
    ]
    agent_actions = [
        {
            "time": "09:15",
            "agent": "InventoryAgent",
            "event": "нашел риск out-of-stock по WB-MOCK-1",
            "status": "warning",
        },
        {
            "time": "09:20",
            "agent": "AdsAgent",
            "event": "предложил снизить ставку ADS-7",
            "status": "warning",
        },
        {
            "time": "09:25",
            "agent": "PromoAgent",
            "event": "заблокировал участие в акции ниже минимальной маржи",
            "status": "critical",
        },
        {
            "time": "09:30",
            "agent": "ContentAgent",
            "event": "подготовил mock-рекомендации для карточки SKU",
            "status": "ok",
        },
    ]
    agents = [
        {"name": "SalesPlanAgent", "module": "План продаж", "status": "ok", "mode": "mock"},
        {"name": "AdsAgent", "module": "Реклама", "status": "warning", "mode": "mock"},
        {"name": "InventoryAgent", "module": "Остатки", "status": "critical", "mode": "mock"},
        {"name": "PromoAgent", "module": "Акции", "status": "warning", "mode": "mock"},
        {"name": "ContentAgent", "module": "Контент", "status": "ok", "mode": "mock"},
        {"name": "FeedbackAgent", "module": "Отзывы", "status": "ok", "mode": "mock"},
        {"name": "AnalyticsAgent", "module": "Аналитика", "status": "ok", "mode": "mock"},
    ]
    audit = [
        {
            "time": "09:15:01",
            "event_type": "agent_alert_created",
            "actor": "InventoryAgent",
            "status": "recorded",
            "detail": "WB-MOCK-1 stock_days=5",
        },
        {
            "time": "09:20:14",
            "event_type": "action_registered",
            "actor": "AdsAgent",
            "status": "recorded",
            "detail": "act-ads-007 requires approval",
        },
        {
            "time": "09:25:33",
            "event_type": "safety_action_evaluated",
            "actor": "SafetyEngine",
            "status": "blocked",
            "detail": "promo margin below minimum",
        },
    ]
    return {
        "system_status": "mock-ready",
        "safety_mode": "SHADOW / safe-mode enabled",
        "alerts": alerts,
        "actions": actions,
        "skus": skus,
        "agent_actions": agent_actions,
        "agents": agents,
        "audit": audit,
        "alerts_count": len(alerts),
        "approval_count": len(
            [action for action in actions if action["status"] == "approval_required"]
        ),
    }


def _context(request: Request, **extra: Any) -> dict[str, Any]:
    data = _mock_dashboard_data()
    data.update(extra)
    data["request"] = request
    return data


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context=_context(request, title="Dashboard")
    )


@router.get("/alerts", response_class=HTMLResponse)
async def dashboard_alerts(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="alerts.html", context=_context(request, title="Alerts")
    )


@router.get("/actions", response_class=HTMLResponse)
async def dashboard_actions(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="actions.html", context=_context(request, title="Actions")
    )


@router.get("/sku/{sku}", response_class=HTMLResponse)
async def dashboard_sku(request: Request, sku: str) -> HTMLResponse:
    selected = SKUIntelligenceService().build_card(sku)
    return templates.TemplateResponse(
        request=request,
        name="sku.html",
        context=_context(request, title=f"SKU {sku}", selected_sku=selected),
    )


@router.get("/agents", response_class=HTMLResponse)
async def dashboard_agents(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="agents.html", context=_context(request, title="Agents")
    )


@router.get("/audit", response_class=HTMLResponse)
async def dashboard_audit(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="audit.html", context=_context(request, title="Audit")
    )
