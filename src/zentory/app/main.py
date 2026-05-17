from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from zentory.api.routers import (
    actions_router,
    analytics_router,
    content_router,
    finance_router,
    health_router,
    learning_router,
    reports_router,
    sku_router,
    supply_router,
    telegram_router,
)
from zentory.app.lifespan import lifespan
from zentory.core.errors import ZentoryError, handle_internal_error
from zentory.web.routes import STATIC_DIR
from zentory.web.routes import router as dashboard_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Zentorybot",
        description="AI operating system for marketplace operations",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(telegram_router)
    app.include_router(actions_router)
    app.include_router(analytics_router)
    app.include_router(content_router)
    app.include_router(finance_router)
    app.include_router(learning_router)
    app.include_router(reports_router)
    app.include_router(sku_router)
    app.include_router(supply_router)
    app.include_router(dashboard_router)
    app.mount(
        "/dashboard/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="dashboard_static",
    )

    @app.exception_handler(ZentoryError)
    async def zentory_exception_handler(_request: Request, exc: ZentoryError) -> JSONResponse:
        return JSONResponse(status_code=400, content=handle_internal_error(exc, source="app"))

    @app.exception_handler(Exception)
    async def generic_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content=handle_internal_error(exc, source="app"))

    return app


app = create_app()
