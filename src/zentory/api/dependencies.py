from functools import lru_cache

from zentory.actions.action_center import ActionCenter
from zentory.actions.registry import ActionRegistry
from zentory.agents.orchestrator import Orchestrator
from zentory.integrations.telegram.client import TelegramClient
from zentory.integrations.telegram.formatter import TelegramFormatter
from zentory.services.audit_service import AuditService
from zentory.services.forecast_service import ForecastService
from zentory.services.idempotency import IdempotencyStore
from zentory.services.reports_service import ReportsService
from zentory.services.rollback_service import RollbackService
from zentory.services.safe_mode import SafeModeService
from zentory.services.telegram_command_service import TelegramCommandService


@lru_cache
def get_audit_service() -> AuditService:
    return AuditService()


@lru_cache
def get_idempotency_store() -> IdempotencyStore:
    return IdempotencyStore()


@lru_cache
def get_safe_mode_service() -> SafeModeService:
    return SafeModeService(enabled=True)


@lru_cache
def get_action_registry() -> ActionRegistry:
    return ActionRegistry(
        audit_service=get_audit_service(),
        idempotency_store=get_idempotency_store(),
        safe_mode=get_safe_mode_service(),
    )


@lru_cache
def get_orchestrator() -> Orchestrator:
    return Orchestrator(action_registry=get_action_registry(), audit_service=get_audit_service())


@lru_cache
def get_action_center() -> ActionCenter:
    return ActionCenter(audit_service=get_audit_service())


def get_reports_service() -> ReportsService:
    return ReportsService()


@lru_cache
def get_rollback_service() -> RollbackService:
    return RollbackService(audit_service=get_audit_service())


@lru_cache
def get_telegram_command_service() -> TelegramCommandService:
    return TelegramCommandService()


@lru_cache
def get_telegram_client() -> TelegramClient:
    return TelegramClient()


@lru_cache
def get_telegram_formatter() -> TelegramFormatter:
    return TelegramFormatter()


@lru_cache
def get_forecast_service() -> ForecastService:
    return ForecastService()
