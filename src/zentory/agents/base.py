from abc import ABC, abstractmethod
from typing import Any

from zentory.actions.schemas import Action


class BaseAgent(ABC):
    name: str
    description: str
    supported_events: tuple[str, ...]

    def can_handle(self, event_type: str) -> bool:
        return "*" in self.supported_events or event_type in self.supported_events

    @abstractmethod
    async def analyze(self, event: dict[str, Any]) -> dict[str, Any]:
        """Analyze incoming event and return structured mock insight."""

    @abstractmethod
    async def propose_actions(self, event: dict[str, Any]) -> list[Action]:
        """Return proposed actions for decision engine."""
