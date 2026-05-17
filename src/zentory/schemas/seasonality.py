from pydantic import BaseModel


class SeasonalityResult(BaseModel):
    sku: str | None = None
    category: str
    month: str
    category_coefficient: float
    month_coefficient: float
    sku_coefficient: float
    seasonality_coefficient: float
    trend_coefficient: float
    mock_mode: bool = True
