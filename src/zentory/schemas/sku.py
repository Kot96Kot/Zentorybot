from zentory.schemas.marketplace import DataSourceLabel, SourceStampedModel


class SKUIdentity(SourceStampedModel):
    sku: str
    nm_id: int | None = None
    vendor_code: str
    marketplace: DataSourceLabel
    product_name: str
    category: str
    brand: str
