from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TeamRoleName(StrEnum):
    MARKETPLACE_MANAGER = "AI Marketplace Manager"
    ANALYST = "AI Analyst"
    ADS_MANAGER = "AI Ads Manager"
    CONTENT_DIRECTOR = "AI Content Director"
    CFO = "AI CFO"
    SUPPLY_MANAGER = "AI Supply Manager"
    COO = "AI COO"
    HUMAN_OWNER = "Human Owner"


class TeamRoleDefinition(BaseModel):
    role: TeamRoleName
    responsibility: str
    input_data: list[str]
    output_result: list[str]
    included_agents: list[str]
    telegram_commands: list[str]
    no_approval_actions: list[str]
    approval_required_actions: list[str]
    mock: bool = True


class TeamRoleResult(BaseModel):
    role: TeamRoleName
    summary: str
    agent_results: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    actions_count: int = 0
    requires_human_approval: bool = False
    next_telegram_commands: list[str] = Field(default_factory=list)
    mock: bool = True
