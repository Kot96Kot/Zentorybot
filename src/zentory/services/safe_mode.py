from zentory.actions.schemas import Action
from zentory.core.enums import ActionStatus
from zentory.core.errors import SafeModeViolationError


class SafeModeService:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def ensure_can_execute(self, action: Action, *, force: bool = False) -> None:
        if self.enabled and not force:
            action.status = ActionStatus.PROPOSED
            raise SafeModeViolationError(
                "Safe mode is enabled: action was proposed but not executed automatically"
            )
