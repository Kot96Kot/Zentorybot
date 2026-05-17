from typing import Any

from zentory.core.logging import get_logger, log_error

logger = get_logger(__name__)


class ZentoryError(Exception):
    """Base application exception."""


class ActionNotFoundError(ZentoryError):
    """Raised when action cannot be found in registry."""


class DuplicateActionError(ZentoryError):
    """Raised when idempotency layer detects a duplicate action."""


class ExternalAPIError(ZentoryError):
    """Raised when an external marketplace or Telegram API call fails."""


class RetryExhaustedError(ZentoryError):
    """Raised when retry attempts are exhausted."""


class SafeModeViolationError(ZentoryError):
    """Raised when code tries to execute an action while safe mode is enabled."""


class TelegramWebhookError(ZentoryError):
    """Raised when Telegram webhook processing fails."""


class TaskProcessingError(ZentoryError):
    """Raised when an internal worker task fails."""


def error_payload(error: Exception, *, source: str) -> dict[str, Any]:
    return {
        "status": "error",
        "source": source,
        "error_type": error.__class__.__name__,
        "detail": str(error),
        "mock": True,
    }


def handle_internal_error(error: Exception, *, source: str) -> dict[str, Any]:
    payload = error_payload(error, source=source)
    log_error(logger, "internal_error_handled", **payload)
    return payload
