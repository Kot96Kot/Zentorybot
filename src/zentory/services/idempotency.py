import hashlib
import json
from collections.abc import Callable
from typing import Any, TypeVar

from zentory.core.errors import DuplicateActionError

T = TypeVar("T")


def idempotency_key(payload: dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(normalized.encode()).hexdigest()


class IdempotencyStore:
    def __init__(self) -> None:
        self._completed: dict[str, Any] = {}

    def exists(self, key: str) -> bool:
        return key in self._completed

    def get(self, key: str) -> Any | None:
        return self._completed.get(key)

    def record(self, key: str, result: Any) -> Any:
        if self.exists(key):
            raise DuplicateActionError(f"Idempotency key {key} has already been completed")
        self._completed[key] = result
        return result

    def execute_once(self, key: str, operation: Callable[[], T]) -> T:
        if self.exists(key):
            raise DuplicateActionError(f"Idempotency key {key} has already been completed")
        result = operation()
        self._completed[key] = result
        return result
