from datetime import date

from zentory.schemas.marketplace import SourceStampedModel


class SalesSnapshot(SourceStampedModel):
    date_from: date
    date_to: date
    orders_qty: int = 0
    sales_qty: int = 0
    revenue: float = 0
    buyout_percent: float = 0
    returns_qty: int = 0
    avg_price: float = 0
