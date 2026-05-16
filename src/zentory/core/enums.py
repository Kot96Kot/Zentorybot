from enum import StrEnum


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ApprovalMode(StrEnum):
    NONE = "NONE"
    SOFT_APPROVAL = "SOFT_APPROVAL"
    HARD_APPROVAL = "HARD_APPROVAL"


class ActionStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class EventSource(StrEnum):
    TELEGRAM = "telegram"
    API = "api"
    SCHEDULER = "scheduler"
    MOCK = "mock"
