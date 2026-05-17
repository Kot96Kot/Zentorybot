__all__ = ["Action", "ActionCenter", "ActionRegistry"]


def __getattr__(name: str) -> object:
    if name == "Action":
        from zentory.actions.schemas import Action

        return Action
    if name == "ActionCenter":
        from zentory.actions.action_center import ActionCenter

        return ActionCenter
    if name == "ActionRegistry":
        from zentory.actions.registry import ActionRegistry

        return ActionRegistry
    raise AttributeError(f"module 'zentory.actions' has no attribute {name!r}")
