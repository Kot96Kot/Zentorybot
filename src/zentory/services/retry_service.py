import asyncio
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from zentory.core.errors import RetryExhaustedError
from zentory.core.logging import get_logger, log_action, log_error

T = TypeVar("T")
logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class RetryConfig:
    attempts: int = 3
    delay_seconds: float = 0.1
    backoff_multiplier: float = 2.0


class RetryService:
    def __init__(self, config: RetryConfig | None = None) -> None:
        self.config = config or RetryConfig()

    async def run(self, operation: Callable[[], T | Any], *, operation_name: str) -> T:
        last_error: Exception | None = None
        delay = self.config.delay_seconds
        for attempt in range(1, self.config.attempts + 1):
            try:
                result = operation()
                if inspect.isawaitable(result):
                    result = await result
                log_action(
                    logger,
                    "retry_operation_succeeded",
                    operation_name=operation_name,
                    attempt=attempt,
                    mock=True,
                )
                return result
            except Exception as exc:  # noqa: BLE001 - retry wrapper must catch external errors
                last_error = exc
                log_error(
                    logger,
                    "retry_operation_failed",
                    operation_name=operation_name,
                    attempt=attempt,
                    error_type=exc.__class__.__name__,
                    detail=str(exc),
                    mock=True,
                )
                if attempt < self.config.attempts:
                    await asyncio.sleep(delay)
                    delay *= self.config.backoff_multiplier
        raise RetryExhaustedError(
            f"Operation {operation_name} failed after {self.config.attempts} attempts"
        ) from last_error
