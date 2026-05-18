from zentory.schemas.platform_modules import FinanceCheck, FinanceCheckerReport


class FinanceCheckerService:
    def build_report(self) -> FinanceCheckerReport:
        checks = [
            FinanceCheck(
                sku="WB-MOCK-1",
                revenue=486_240.0,
                gross_margin_percent=24.5,
                drr_percent=17.8,
                contribution_profit=32_860.0,
                verdict="watch",
                recommendations=[
                    "Не повышать рекламные ставки до пополнения склада.",
                    "Проверить комиссию и логистику перед скидкой.",
                ],
            ),
            FinanceCheck(
                sku="ZNT-YM-003",
                revenue=7_920.0,
                gross_margin_percent=9.0,
                drr_percent=0.0,
                contribution_profit=410.0,
                verdict="hold",
                recommendations=["Не закупать партию, пока Learning Loop не подтвердит спрос."],
            ),
        ]
        return FinanceCheckerReport(
            checks=checks,
            total_contribution_profit=sum(check.contribution_profit for check in checks),
        )
