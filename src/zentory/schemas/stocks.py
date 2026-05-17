from pydantic import Field

from zentory.schemas.marketplace import SourceStampedModel


class StockSnapshot(SourceStampedModel):
    total_stock: int = 0
    stock_by_warehouse: dict[str, int] = Field(default_factory=dict)
    stock_by_region: dict[str, int] = Field(default_factory=dict)
    days_of_coverage: float | None = None
    out_of_stock: bool = False
