from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Marketplace(StrEnum):
    WILDBERRIES = "wildberries"
    OZON = "ozon"
    YANDEX_MARKET = "yandex_market"


class ABCClass(StrEnum):
    A = "A"
    B = "B"
    C = "C"


class ForecastABCItem(BaseModel):
    sku: str
    marketplace: Marketplace
    revenue_share_percent: float
    units_forecast_14d: int
    abc_class: ABCClass
    stockout_risk: bool
    recommended_action: str


class ForecastABCReport(BaseModel):
    horizon_days: int = 14
    items: list[ForecastABCItem]
    summary: dict[str, int]
    mock: bool = True


class SupplyLocalizationItem(BaseModel):
    sku: str
    source_warehouse: str
    target_warehouse: str
    target_region: str
    transfer_units: int
    expected_coverage_days: float
    reason: str


class SupplyLocalizationPlan(BaseModel):
    items: list[SupplyLocalizationItem]
    blocked_actions: list[str] = Field(default_factory=list)
    mock: bool = True


class ContentCTRExperiment(BaseModel):
    sku: str
    current_ctr_percent: float
    target_ctr_percent: float
    hypothesis: str
    title_variant: str
    first_screen_variant: str
    safety_note: str


class ContentCTRFactoryReport(BaseModel):
    experiments: list[ContentCTRExperiment]
    mock: bool = True


class FinanceCheck(BaseModel):
    sku: str
    revenue: float
    gross_margin_percent: float
    drr_percent: float
    contribution_profit: float
    verdict: str
    recommendations: list[str]


class FinanceCheckerReport(BaseModel):
    checks: list[FinanceCheck]
    total_contribution_profit: float
    mock: bool = True


class LearningLoopSignal(BaseModel):
    source_module: str
    metric: str
    before: float
    after: float
    insight: str
    next_rule_update: str


class LearningLoopReport(BaseModel):
    signals: list[LearningLoopSignal]
    mock: bool = True


class DataContractField(BaseModel):
    name: str
    field_type: str
    required: bool = True
    description: str


class DataContract(BaseModel):
    name: str
    version: str
    owner: str
    fields: list[DataContractField]
    safety_constraints: list[str] = Field(default_factory=list)


class DataContractsReport(BaseModel):
    contracts: list[DataContract]
    mock: bool = True


class PlatformModulesSnapshot(BaseModel):
    forecast_abc: ForecastABCReport
    supply_localization: SupplyLocalizationPlan
    content_ctr_factory: ContentCTRFactoryReport
    finance_checker: FinanceCheckerReport
    learning_loop: LearningLoopReport
    data_contracts: DataContractsReport

    def to_manager_summary(self) -> dict[str, Any]:
        return {
            "forecast_items": len(self.forecast_abc.items),
            "supply_moves": len(self.supply_localization.items),
            "content_experiments": len(self.content_ctr_factory.experiments),
            "finance_checks": len(self.finance_checker.checks),
            "learning_signals": len(self.learning_loop.signals),
            "contracts": [contract.name for contract in self.data_contracts.contracts],
        }
