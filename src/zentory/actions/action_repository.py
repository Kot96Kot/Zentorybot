from zentory.core.enums import ActionStatus
from zentory.core.errors import ActionNotFoundError
from zentory.schemas.actions import ActionRecord


class ActionRepository:
    def __init__(self) -> None:
        self._actions: dict[str, ActionRecord] = {}

    def save(self, action: ActionRecord) -> ActionRecord:
        self._actions[action.action_id] = action
        return action

    def get(self, action_id: str) -> ActionRecord:
        try:
            return self._actions[action_id]
        except KeyError as exc:
            raise ActionNotFoundError(f"Action {action_id} not found") from exc

    def update_status(self, action_id: str, status: ActionStatus) -> ActionRecord:
        action = self.get(action_id)
        action.status = status
        self.save(action)
        return action

    def list_pending(self) -> list[ActionRecord]:
        return [
            action
            for action in self._sorted_recent()
            if action.status in {ActionStatus.PROPOSED, ActionStatus.APPROVED}
        ]

    def list_recent(self, *, limit: int = 20) -> list[ActionRecord]:
        return self._sorted_recent()[:limit]

    def _sorted_recent(self) -> list[ActionRecord]:
        return sorted(self._actions.values(), key=lambda action: action.created_at, reverse=True)
