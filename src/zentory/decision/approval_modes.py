from enum import StrEnum


class AutomationMode(StrEnum):
    SHADOW = "SHADOW"
    ASSISTANT = "ASSISTANT"
    SEMI_AUTO = "SEMI_AUTO"
    AUTO = "AUTO"


HARD_APPROVAL_RISKS = {"HIGH", "CRITICAL"}
