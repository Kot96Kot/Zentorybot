from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class DataSourceLabel(StrEnum):
    MOCK = "MOCK"
    WB = "WB"
    OZON = "OZON"
    YANDEX_MARKET = "YANDEX_MARKET"
    MANUAL = "MANUAL"


class SourceStampedModel(BaseModel):
    source: DataSourceLabel = DataSourceLabel.MOCK
    mock: bool = True

    @model_validator(mode="after")
    def validate_mock_source(self) -> "SourceStampedModel":
        if self.mock and self.source != DataSourceLabel.MOCK:
            raise ValueError("mock data must use source=MOCK")
        return self


class MarketplaceAccount(SourceStampedModel):
    account_id: str
    marketplace: DataSourceLabel
    seller_name: str
    legal_name: str | None = None
    is_active: bool = True
    metadata: dict[str, str] = Field(default_factory=dict)
