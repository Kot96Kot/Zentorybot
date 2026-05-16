from abc import ABC, abstractmethod

from zentory.actions.schemas import Action


class BaseActionHandler(ABC):
    action_type: str

    @abstractmethod
    async def execute(self, action: Action) -> Action:
        """Execute action through marketplace adapter."""
