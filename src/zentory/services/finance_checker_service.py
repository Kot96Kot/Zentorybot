from zentory.schemas.finance import (
    FinanceCheckReport,
    FinanceIssue,
    FinanceSkuInput,
    FinanceStatus,
    PnLReport,
    UnitFinanceResult,
)
from zentory.services.dds_check_service import DDSCheckService
from zentory.services.pnl_check_service import PnLCheckService
from zentory.services.unit_profit_service import UnitProfitService


class FinanceCheckerService:
    def __init__(
        self,
        pnl_service: PnLCheckService | None = None,
        dds_service: DDSCheckService | None = None,
        unit_profit_service: UnitProfitService | None = None,
    ) -> None:
        self.pnl_service = pnl_service or PnLCheckService()
        self.dds_service = dds_service or DDSCheckService()
        self.unit_profit_service = unit_profit_service or UnitProfitService()

    def build_mock_rows(self) -> list[FinanceSkuInput]:
        return [
            FinanceSkuInput(
                sku="ZNT-PROFIT-001",
                revenue=120_000,
                commission=18_000,
                logistics=7_500,
                acquiring=2_400,
                advertising=12_000,
                cost=52_000,
                storage=1_100,
                penalties=0,
                return_logistics=1_500,
                taxes=7_200,
                price=1_500,
                minimum_price=1_250,
                report_profit=18_300,
                internal_profit=18_300,
                previous_expenses=84_000,
                current_expenses=101_700,
            ),
            FinanceSkuInput(
                sku="ZNT-LOSS-002",
                revenue=48_000,
                commission=0,
                logistics=0,
                acquiring=960,
                advertising=34_000,
                cost=21_000,
                storage=2_500,
                penalties=3_000,
                return_logistics=2_400,
                taxes=0,
                price=790,
                minimum_price=920,
                report_profit=-15_000,
                internal_profit=-15_860,
                previous_expenses=26_000,
                current_expenses=63_860,
            ),
            FinanceSkuInput(
                sku="ZNT-NOCOST-003",
                revenue=30_000,
                commission=4_500,
                logistics=2_100,
                acquiring=600,
                advertising=5_000,
                cost=0,
                storage=800,
                penalties=0,
                return_logistics=900,
                taxes=1_800,
                price=1_200,
                minimum_price=900,
                report_profit=14_200,
                internal_profit=14_300,
                previous_expenses=9_000,
                current_expenses=15_700,
            ),
        ]

    def check(self) -> FinanceCheckReport:
        rows = self.build_mock_rows()
        pnl = self.pnl(rows)
        pnl_issues = self.pnl_service.check(rows)
        dds = self.dds_service.check(
            cash_in=pnl.total_revenue,
            cash_out=pnl.total_expenses,
            opening_cash=25_000,
            actual_closing_cash=25_500,
        )
        issues = pnl_issues + dds.issues
        status = self._status_from_issues(issues)
        return FinanceCheckReport(
            status=status,
            issues=issues,
            pnl=pnl,
            dds=dds,
            recommendation=self._recommendation(status, issues),
            safety_notes=[
                "Не проводить платежи автоматически.",
                "Не изменять финальные отчеты автоматически.",
                "Только проверка, подсветка аномалий и рекомендации.",
                "Все данные mock.",
            ],
            mock_mode=True,
        )

    def pnl(self, rows: list[FinanceSkuInput] | None = None) -> PnLReport:
        return self.pnl_service.build_report(rows or self.build_mock_rows())

    def unit(self, sku: str) -> UnitFinanceResult | None:
        for row in self.build_mock_rows():
            if row.sku == sku:
                return self.unit_profit_service.calculate_finance(row)
        return None

    @staticmethod
    def _status_from_issues(issues: list[FinanceIssue]) -> FinanceStatus:
        if any(issue.status == FinanceStatus.CRITICAL for issue in issues):
            return FinanceStatus.CRITICAL
        if issues:
            return FinanceStatus.WARNING
        return FinanceStatus.OK

    @staticmethod
    def _recommendation(status: FinanceStatus, issues: list[FinanceIssue]) -> str:
        if status == FinanceStatus.CRITICAL:
            return "Остановить решения по цене/рекламе и вручную проверить critical SKU."
        if status == FinanceStatus.WARNING:
            return "Сверить предупреждения перед закрытием управленческого отчета."
        return "Финансовые mock-расчеты сходятся, можно наблюдать."
