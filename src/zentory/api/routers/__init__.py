from zentory.api.routers.actions import router as actions_router
from zentory.api.routers.analytics import router as analytics_router
from zentory.api.routers.content import router as content_router
from zentory.api.routers.finance import router as finance_router
from zentory.api.routers.health import router as health_router
from zentory.api.routers.learning import router as learning_router
from zentory.api.routers.reports import router as reports_router
from zentory.api.routers.sku import router as sku_router
from zentory.api.routers.supply import router as supply_router
from zentory.api.routers.telegram import router as telegram_router

__all__ = [
    "actions_router",
    "analytics_router",
    "content_router",
    "finance_router",
    "health_router",
    "learning_router",
    "reports_router",
    "sku_router",
    "supply_router",
    "telegram_router",
]
