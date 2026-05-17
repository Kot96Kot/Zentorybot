from zentory.schemas.finance import FinanceIssueType, FinanceSkuInput, FinanceStatus
from zentory.services.pnl_check_service import PnLCheckService


def _row(**overrides: object) -> FinanceSkuInput:
    data = {
        "sku": "SKU-PNL",
        "revenue": 1000.0,
        "commission": 100.0,
        "logistics": 50.0,
        "acquiring": 20.0,
        "advertising": 80.0,
        "cost": 400.0,
        "storage": 10.0,
        "penalties": 0.0,
        "return_logistics": 15.0,
        "taxes": 60.0,
        "price": 1000.0,
        "minimum_price": 700.0,
        "report_profit": 265.0,
        "internal_profit": 265.0,
        "previous_expenses": 700.0,
        "current_expenses": 735.0,
    }
    data.update(overrides)
    return FinanceSkuInput(**data)


def test_pnl_check_detects_missing_cost_taxes_and_expense_spike() -> None:
    row = _row(cost=0, taxes=0, previous_expenses=100, current_expenses=250)

    issues = PnLCheckService().check([row])
    issue_types = {issue.issue_type for issue in issues}

    assert FinanceIssueType.MISSING_COST in issue_types
    assert FinanceIssueType.MISSING_TAXES in issue_types
    assert FinanceIssueType.EXPENSE_SPIKE in issue_types
    assert all(issue.needs_human_check for issue in issues)


def test_pnl_report_aggregates_units_and_status() -> None:
    service = PnLCheckService()

    report = service.build_report([_row(), _row(sku="SKU-LOSS", revenue=100, cost=200)])

    assert len(report.units) == 2
    assert report.total_revenue == 1100.0
    assert report.status == FinanceStatus.CRITICAL
