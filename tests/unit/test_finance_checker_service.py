from zentory.schemas.finance import FinanceIssueType, FinanceStatus
from zentory.services.finance_checker_service import FinanceCheckerService


def test_finance_checker_finds_required_mock_anomalies() -> None:
    report = FinanceCheckerService().check()

    issue_types = {issue.issue_type for issue in report.issues}
    assert report.status == FinanceStatus.CRITICAL
    assert FinanceIssueType.NEGATIVE_MARGIN in issue_types
    assert FinanceIssueType.PRICE_BELOW_MINIMUM in issue_types
    assert FinanceIssueType.ADS_ATE_PROFIT in issue_types
    assert FinanceIssueType.MISSING_COMMISSION in issue_types
    assert FinanceIssueType.MISSING_LOGISTICS in issue_types
    assert FinanceIssueType.EXPENSES_OVER_REVENUE in issue_types
    assert FinanceIssueType.REPORT_INTERNAL_MISMATCH in issue_types
    assert FinanceIssueType.EXPENSE_SPIKE in issue_types
    assert FinanceIssueType.MISSING_COST in issue_types
    assert FinanceIssueType.MISSING_TAXES in issue_types
    assert report.safety_notes


def test_finance_checker_returns_unit_by_sku() -> None:
    unit = FinanceCheckerService().unit("ZNT-PROFIT-001")

    assert unit is not None
    assert unit.sku == "ZNT-PROFIT-001"
    assert unit.profit > 0
