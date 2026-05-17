import pytest
from pydantic import ValidationError

from zentory.schemas.ads import AdsSnapshot
from zentory.schemas.marketplace import DataSourceLabel, MarketplaceAccount
from zentory.schemas.reviews import ReviewSnapshot
from zentory.schemas.sales import SalesSnapshot
from zentory.schemas.sku import SKUIdentity
from zentory.schemas.stocks import StockSnapshot
from zentory.schemas.unit_economics import UnitEconomicsSnapshot
from zentory.services.data_normalization_service import DataNormalizationService


def test_core_data_contracts_accept_mock_source() -> None:
    identity = SKUIdentity(
        sku="SKU-1",
        nm_id=123,
        vendor_code="V-1",
        marketplace=DataSourceLabel.MOCK,
        product_name="Mock product",
        category="mock",
        brand="Zentory",
    )
    sales = SalesSnapshot(
        date_from="2026-01-01",
        date_to="2026-01-31",
        orders_qty=10,
        sales_qty=8,
        revenue=8_000,
        buyout_percent=0.8,
        returns_qty=2,
        avg_price=1_000,
    )
    stock = StockSnapshot(
        total_stock=15,
        stock_by_warehouse={"W1": 10, "W2": 5},
        stock_by_region={"Center": 15},
        days_of_coverage=12.5,
        out_of_stock=False,
    )
    ads = AdsSnapshot(
        impressions=1_000,
        clicks=40,
        ctr=0.04,
        spend=500,
        orders=5,
        revenue=5_000,
        drr=0.1,
        cpm=100,
        cpc=12.5,
        campaign_id="C-1",
    )
    reviews = ReviewSnapshot(rating=4.7, reviews_count=20, latest_reviews=["ok"])
    unit = UnitEconomicsSnapshot(
        price=1_000,
        cost=400,
        commission=150,
        logistics=100,
        acquiring=20,
        ads_cost=50,
        tax=60,
        storage=10,
        return_logistics=20,
        profit=190,
        margin_percent=0.19,
    )
    account = MarketplaceAccount(
        account_id="mock-account",
        marketplace=DataSourceLabel.MOCK,
        seller_name="Mock Seller",
    )

    assert identity.source == DataSourceLabel.MOCK
    assert sales.source == DataSourceLabel.MOCK
    assert stock.total_stock == 15
    assert ads.campaign_id == "C-1"
    assert reviews.latest_reviews == ["ok"]
    assert unit.margin_percent == 0.19
    assert account.mock is True


def test_mock_data_must_have_mock_source() -> None:
    with pytest.raises(ValidationError, match="mock data must use source=MOCK"):
        SKUIdentity(
            sku="SKU-1",
            nm_id=123,
            vendor_code="V-1",
            marketplace=DataSourceLabel.WB,
            product_name="Real-looking mock product",
            category="category",
            brand="Brand",
            source=DataSourceLabel.WB,
            mock=True,
        )


def test_real_data_can_use_real_source_when_not_mock() -> None:
    identity = SKUIdentity(
        sku="WB-1",
        nm_id=123,
        vendor_code="WB-1",
        marketplace=DataSourceLabel.WB,
        product_name="WB product",
        category="category",
        brand="Brand",
        source=DataSourceLabel.WB,
        mock=False,
    )

    assert identity.source == DataSourceLabel.WB
    assert identity.mock is False


def test_normalization_warns_when_mock_and_real_are_mixed() -> None:
    identity = SKUIdentity(
        sku="WB-1",
        nm_id=123,
        vendor_code="WB-1",
        marketplace=DataSourceLabel.WB,
        product_name="WB product",
        category="category",
        brand="Brand",
        source=DataSourceLabel.WB,
        mock=False,
    )
    sales = SalesSnapshot(
        date_from="2026-01-01",
        date_to="2026-01-31",
        sales_qty=10,
        revenue=10_000,
        source=DataSourceLabel.MOCK,
        mock=True,
    )

    normalized = DataNormalizationService().normalize_sku_data(identity=identity, sales=sales)

    assert normalized.warnings
    assert "Real data is mixed with mock data" in normalized.warnings[0]


def test_normalize_mock_sku_sets_all_sources_to_mock() -> None:
    normalized = DataNormalizationService().normalize_mock_sku(
        {
            "sku": "MOCK-1",
            "nm_id": 1,
            "vendor_code": "V-MOCK-1",
            "product_name": "Mock SKU",
            "category": "cosmetics",
            "brand": "Zentory",
            "warehouse_name": "W1",
            "region": "Center",
            "stock_qty": 12,
            "sales_qty_30d": 6,
            "revenue_30d": 6_000,
            "buyout_percent": 0.9,
            "price": 1_000,
            "cost": 500,
            "advertising_spend": 200,
        }
    )

    assert normalized.identity.source == DataSourceLabel.MOCK
    assert normalized.sales and normalized.sales.source == DataSourceLabel.MOCK
    assert normalized.stock and normalized.stock.source == DataSourceLabel.MOCK
    assert normalized.ads and normalized.ads.source == DataSourceLabel.MOCK
    assert normalized.reviews and normalized.reviews.source == DataSourceLabel.MOCK
    assert normalized.unit_economics
    assert normalized.unit_economics.source == DataSourceLabel.MOCK
    assert normalized.warnings == []
