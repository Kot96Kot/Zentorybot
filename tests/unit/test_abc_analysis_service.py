from pytest import approx

from zentory.schemas.abc import ABCAnalysisInput, ABCClass, ABCMetric
from zentory.services.abc_analysis_service import ABCAnalysisService


def test_abc_shares_cumulative_and_classes_are_correct() -> None:
    items = [
        ABCAnalysisInput(sku="A", product_name="A", revenue=70, profit=30, sales_qty=70),
        ABCAnalysisInput(sku="B", product_name="B", revenue=20, profit=20, sales_qty=20),
        ABCAnalysisInput(sku="C", product_name="C", revenue=10, profit=10, sales_qty=10),
    ]

    report = ABCAnalysisService().analyze(items, metric=ABCMetric.REVENUE)

    assert [row.sku for row in report.rows] == ["A", "B", "C"]
    assert report.rows[0].share_percent == approx(70)
    assert [row.abc_class for row in report.rows] == [ABCClass.A, ABCClass.B, ABCClass.C]
    assert all(
        current >= previous
        for previous, current in zip(
            [row.cumulative_share_percent for row in report.rows],
            [row.cumulative_share_percent for row in report.rows][1:],
            strict=False,
        )
    )
    assert sum(row.share_percent for row in report.rows) == approx(100)


def test_abc_can_use_profit_and_sales_qty_metrics() -> None:
    items = [
        ABCAnalysisInput(sku="A", product_name="A", revenue=1, profit=5, sales_qty=20),
        ABCAnalysisInput(sku="B", product_name="B", revenue=10, profit=30, sales_qty=3),
    ]

    profit_report = ABCAnalysisService().analyze(items, metric="profit")
    qty_report = ABCAnalysisService().analyze(items, metric="sales_qty")

    assert profit_report.rows[0].sku == "B"
    assert qty_report.rows[0].sku == "A"
