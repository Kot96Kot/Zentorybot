from zentory.schemas.finance import FinanceSkuInput, FinanceStatus
from zentory.services.unit_profit_service import UnitProfitService


def _row(**overrides: object) -> FinanceSkuInput:
    data = {
        "sku": "SKU-1",
        "revenue": 1000.0,
        "commission": 100.0,
        "logistics": 50.0,
        "acquiring": 20.0,
        "advertising": 80.0,
        "cost": 400.0,
        "storage": 10.0,
        "penalties": 5.0,
        "return_logistics": 15.0,
        "taxes": 60.0,
        "price": 1000.0,
        "minimum_price": 700.0,
        "report_profit": 260.0,
        "internal_profit": 260.0,
        "previous_expenses": 700.0,
        "current_expenses": 740.0,
    }
    data.update(overrides)
    return FinanceSkuInput(**data)


def test_unit_profit_uses_full_sku_profit_formula() -> None:
    result = UnitProfitService().calculate_finance(_row())

    assert result.total_expenses == 740.0
    assert result.profit == 260.0
    assert result.margin_percent == 0.26
    assert result.status == FinanceStatus.OK


def test_unit_profit_marks_price_below_minimum_as_critical() -> None:
    result = UnitProfitService().calculate_finance(_row(price=650.0, minimum_price=700.0))

    assert result.status == FinanceStatus.CRITICAL
