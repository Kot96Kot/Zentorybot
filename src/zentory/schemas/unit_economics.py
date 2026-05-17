from zentory.schemas.marketplace import SourceStampedModel


class UnitEconomicsSnapshot(SourceStampedModel):
    price: float = 0
    cost: float = 0
    commission: float = 0
    logistics: float = 0
    acquiring: float = 0
    ads_cost: float = 0
    tax: float = 0
    storage: float = 0
    return_logistics: float = 0
    profit: float = 0
    margin_percent: float = 0
