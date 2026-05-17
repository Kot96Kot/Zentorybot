from pydantic import BaseModel


class SeasonalityResult(BaseModel):
    sku: str | None = None
    category: str
    month: str
    seasonality_coefficient: float
    trend_coefficient: float
    mock_mode: bool = True
