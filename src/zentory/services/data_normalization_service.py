from typing import Any

from pydantic import BaseModel, Field

from zentory.schemas.ads import AdsSnapshot
from zentory.schemas.marketplace import DataSourceLabel
from zentory.schemas.reviews import ReviewSnapshot
from zentory.schemas.sales import SalesSnapshot
from zentory.schemas.sku import SKUIdentity
from zentory.schemas.stocks import StockSnapshot
from zentory.schemas.unit_economics import UnitEconomicsSnapshot


class NormalizedSKUData(BaseModel):
    identity: SKUIdentity
    sales: SalesSnapshot | None = None
    stock: StockSnapshot | None = None
    ads: AdsSnapshot | None = None
    reviews: ReviewSnapshot | None = None
    unit_economics: UnitEconomicsSnapshot | None = None
    warnings: list[str] = Field(default_factory=list)


class DataNormalizationService:
    def normalize_sku_data(
        self,
        *,
        identity: SKUIdentity,
        sales: SalesSnapshot | None = None,
        stock: StockSnapshot | None = None,
        ads: AdsSnapshot | None = None,
        reviews: ReviewSnapshot | None = None,
        unit_economics: UnitEconomicsSnapshot | None = None,
    ) -> NormalizedSKUData:
        parts = [identity, sales, stock, ads, reviews, unit_economics]
        warnings = self._source_warnings([part for part in parts if part is not None])
        return NormalizedSKUData(
            identity=identity,
            sales=sales,
            stock=stock,
            ads=ads,
            reviews=reviews,
            unit_economics=unit_economics,
            warnings=warnings,
        )

    def normalize_mock_sku(self, raw: dict[str, Any]) -> NormalizedSKUData:
        sku = str(raw.get("sku", "MOCK-SKU"))
        marketplace = DataSourceLabel.MOCK
        identity = SKUIdentity(
            sku=sku,
            nm_id=raw.get("nm_id"),
            vendor_code=str(raw.get("vendor_code", sku)),
            marketplace=marketplace,
            product_name=str(raw.get("product_name", "Mock product")),
            category=str(raw.get("category", "mock")),
            brand=str(raw.get("brand", "Zentory")),
            source=DataSourceLabel.MOCK,
            mock=True,
        )
        stock_by_warehouse = raw.get("stock_by_warehouse") or {
            str(raw.get("warehouse_name", "mock_warehouse")): int(raw.get("stock_qty", 0))
        }
        stock_by_region = raw.get("stock_by_region") or {
            str(raw.get("region", "mock_region")): sum(stock_by_warehouse.values())
        }
        stock = StockSnapshot(
            total_stock=int(raw.get("total_stock", sum(stock_by_warehouse.values()))),
            stock_by_warehouse=stock_by_warehouse,
            stock_by_region=stock_by_region,
            days_of_coverage=raw.get("days_of_coverage"),
            out_of_stock=bool(raw.get("out_of_stock", False)),
            source=DataSourceLabel.MOCK,
            mock=True,
        )
        sales = SalesSnapshot(
            date_from=raw.get("date_from", "2026-01-01"),
            date_to=raw.get("date_to", "2026-01-30"),
            orders_qty=int(raw.get("orders_qty", raw.get("sales_qty_30d", 0))),
            sales_qty=int(raw.get("sales_qty", raw.get("sales_qty_30d", 0))),
            revenue=float(raw.get("revenue", raw.get("revenue_30d", 0))),
            buyout_percent=float(raw.get("buyout_percent", 0)),
            returns_qty=int(raw.get("returns_qty", 0)),
            avg_price=float(raw.get("avg_price", raw.get("price", 0))),
            source=DataSourceLabel.MOCK,
            mock=True,
        )
        ads = AdsSnapshot(
            impressions=int(raw.get("impressions", 0)),
            clicks=int(raw.get("clicks", 0)),
            ctr=float(raw.get("ctr", 0)),
            spend=float(raw.get("advertising_spend", raw.get("spend", 0))),
            orders=int(raw.get("ad_orders", 0)),
            revenue=float(raw.get("ad_revenue", 0)),
            drr=float(raw.get("drr", 0)),
            cpm=raw.get("cpm"),
            cpc=raw.get("cpc"),
            campaign_id=raw.get("campaign_id"),
            source=DataSourceLabel.MOCK,
            mock=True,
        )
        unit_economics = UnitEconomicsSnapshot(
            price=float(raw.get("price", 0)),
            cost=float(raw.get("cost", 0)),
            commission=float(raw.get("commission", 0)),
            logistics=float(raw.get("logistics", 0)),
            acquiring=float(raw.get("acquiring", 0)),
            ads_cost=float(raw.get("advertising_spend", raw.get("ads_cost", 0))),
            tax=float(raw.get("tax", 0)),
            storage=float(raw.get("storage", 0)),
            return_logistics=float(raw.get("return_logistics", 0)),
            profit=float(raw.get("profit", 0)),
            margin_percent=float(raw.get("margin_percent", 0)),
            source=DataSourceLabel.MOCK,
            mock=True,
        )
        reviews = ReviewSnapshot(
            rating=float(raw.get("rating", 0)),
            reviews_count=int(raw.get("reviews_count", 0)),
            negative_reviews_count=int(raw.get("negative_reviews_count", 0)),
            unanswered_reviews_count=int(raw.get("unanswered_reviews_count", 0)),
            latest_reviews=list(raw.get("latest_reviews", [])),
            source=DataSourceLabel.MOCK,
            mock=True,
        )
        return self.normalize_sku_data(
            identity=identity,
            sales=sales,
            stock=stock,
            ads=ads,
            reviews=reviews,
            unit_economics=unit_economics,
        )

    @staticmethod
    def _source_warnings(parts: list[Any]) -> list[str]:
        sources = {part.source for part in parts}
        if DataSourceLabel.MOCK in sources and len(sources) > 1:
            real_sources = sorted(
                source.value for source in sources if source != DataSourceLabel.MOCK
            )
            return [
                "Real data is mixed with mock data: "
                f"MOCK + {', '.join(real_sources)}. Verify before using recommendations."
            ]
        return []
