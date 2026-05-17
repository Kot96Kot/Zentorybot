from enum import StrEnum

from pydantic import BaseModel, Field


class ABCMetric(StrEnum):
    REVENUE = "revenue"
    PROFIT = "profit"
    SALES_QTY = "sales_qty"


class ABCClass(StrEnum):
    A = "A"
    B = "B"
    C = "C"


class ABCAnalysisInput(BaseModel):
    sku: str
    product_name: str
    revenue: float = 0
    profit: float = 0
    sales_qty: int = 0
    mock: bool = True


class ABCAnalysisRow(BaseModel):
    sku: str
    product_name: str
    metric_value: float
    share_percent: float
    cumulative_share_percent: float
    abc_class: ABCClass
    rank: int
    mock: bool = True


class ABCClassSummary(BaseModel):
    abc_class: ABCClass
    sku_count: int
    share_percent: float


class ABCAnalysisReport(BaseModel):
    metric: ABCMetric
    total_metric: float
    rows: list[ABCAnalysisRow] = Field(default_factory=list)
    class_summary: list[ABCClassSummary] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    mock_mode: bool = True
