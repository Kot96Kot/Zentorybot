from typing import Any

from zentory.schemas.actions import ActionPreview, ActionRecord


class ActionPreviewBuilder:
    def build(self, action: ActionRecord) -> ActionPreview:
        return ActionPreview(
            action_id=action.action_id,
            title=action.title,
            proposed_by=action.agent_name,
            reason=action.explanation or action.description,
            risk_level=action.risk_level,
            approval_mode=action.approval_mode,
            data_used=action.evidence,
            changes=self._changes(action.before_state, action.after_state),
            rollback_available=action.rollback_available,
            buttons=[
                {"text": "Approve", "command": f"/approve {action.action_id}"},
                {"text": "Reject", "command": f"/reject {action.action_id}"},
            ],
        )

    @staticmethod
    def _changes(
        before_state: dict[str, Any], after_state: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        keys = sorted(set(before_state) | set(after_state))
        return {
            key: {"before": before_state.get(key), "after": after_state.get(key)}
            for key in keys
            if before_state.get(key) != after_state.get(key)
        }
