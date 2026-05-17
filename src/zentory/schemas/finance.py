from enum import StrEnum

from pydantic import BaseModel, Field


class FinanceStatus(StrEnum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class FinanceIssueType(StrEnum):
    NEGATIVE_MARGIN = "negative_margin"
    PRICE_BELOW_MINIMUM = "price_below_minimum"
    ADS_ATE_PROFIT = "ads_ate_profit"
    MISSING_COMMISSION = "missing_commission"
    MISSING_LOGISTICS = "missing_logistics"
    EXPENSES_OVER_REVENUE = "expenses_over_revenue"
    REPORT_INTERNAL_MISMATCH = "report_internal_mismatch"
    EXPENSE_SPIKE = "expense_spike"
    MISSING_COST = "missing_cost"
    MISSING_TAXES = "missing_taxes"
    CASH_FLOW_MISMATCH = "cash_flow_mismatch"


class FinanceSkuInput(BaseModel):
    sku: str
    revenue: float
    commission: float
    logistics: float
    acquiring: float
    advertising: float
    cost: float
    storage: float
    penalties: float
    return_logistics: float
    taxes: float
    price: float
    minimum_price: float
    report_profit: float
    internal_profit: float
    previous_expenses: float
    current_expenses: float
    mock_mode: bool = True


class UnitFinanceResult(BaseModel):
    sku: str
    revenue: float
    commission: float
    logistics: float
    acquiring: float
    advertising: float
    cost: float
    storage: float
    penalties: float
    return_logistics: float
    taxes: float
    total_expenses: float
    profit: float
    margin_percent: float
    minimum_price: float
    price: float
    status: FinanceStatus
    mock_mode: bool = True


class FinanceIssue(BaseModel):
    status: FinanceStatus
    issue_type: FinanceIssueType
    affected_sku: str
    expected_value: float | str | None
    actual_value: float | str | None
    difference: float | None
    recommendation: str
    needs_human_check: bool = True
    mock_mode: bool = True


class PnLReport(BaseModel):
    units: list[UnitFinanceResult] = Field(default_factory=list)
    total_revenue: float
    total_expenses: float
    total_profit: float
    margin_percent: float
    status: FinanceStatus
    mock_mode: bool = True


class DDSCheckResult(BaseModel):
    status: FinanceStatus
    issues: list[FinanceIssue] = Field(default_factory=list)
    cash_in: float
    cash_out: float
    expected_closing_cash: float
    actual_closing_cash: float
    difference: float
    mock_mode: bool = True


class FinanceCheckReport(BaseModel):
    status: FinanceStatus
    issues: list[FinanceIssue] = Field(default_factory=list)
    pnl: PnLReport
    dds: DDSCheckResult
    recommendation: str
    safety_notes: list[str] = Field(default_factory=list)
    mock_mode: bool = True
