from zentory.schemas.finance import (
    FinanceIssue,
    FinanceIssueType,
    FinanceSkuInput,
    FinanceStatus,
    PnLReport,
    UnitFinanceResult,
)
from zentory.services.unit_profit_service import UnitProfitService


class PnLCheckService:
    def __init__(self, unit_profit_service: UnitProfitService | None = None) -> None:
        self.unit_profit_service = unit_profit_service or UnitProfitService()

    def build_report(self, rows: list[FinanceSkuInput]) -> PnLReport:
        units = [self.unit_profit_service.calculate_finance(row) for row in rows]
        total_revenue = round(sum(unit.revenue for unit in units), 2)
        total_expenses = round(sum(unit.total_expenses for unit in units), 2)
        total_profit = round(sum(unit.profit for unit in units), 2)
        margin = round(total_profit / total_revenue, 4) if total_revenue > 0 else -1
        status = FinanceStatus.OK
        if any(unit.status == FinanceStatus.CRITICAL for unit in units):
            status = FinanceStatus.CRITICAL
        elif any(unit.status == FinanceStatus.WARNING for unit in units):
            status = FinanceStatus.WARNING
        return PnLReport(
            units=units,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            total_profit=total_profit,
            margin_percent=margin,
            status=status,
            mock_mode=True,
        )

    def check(self, rows: list[FinanceSkuInput]) -> list[FinanceIssue]:
        issues: list[FinanceIssue] = []
        for row in rows:
            unit = self.unit_profit_service.calculate_finance(row)
            issues.extend(self._row_issues(row, unit))
        return issues

    def _row_issues(self, row: FinanceSkuInput, unit: UnitFinanceResult) -> list[FinanceIssue]:
        issues: list[FinanceIssue] = []
        if unit.margin_percent < 0:
            issues.append(
                self._issue(
                    FinanceStatus.CRITICAL,
                    FinanceIssueType.NEGATIVE_MARGIN,
                    row.sku,
                    "margin >= 0",
                    unit.margin_percent,
                    unit.margin_percent,
                    "Остановить снижение цены/акции и проверить себестоимость и расходы.",
                )
            )
        if row.price < row.minimum_price:
            issues.append(
                self._issue(
                    FinanceStatus.CRITICAL,
                    FinanceIssueType.PRICE_BELOW_MINIMUM,
                    row.sku,
                    row.minimum_price,
                    row.price,
                    round(row.price - row.minimum_price, 2),
                    "Поднять цену выше минимальной или пересчитать обязательные расходы.",
                )
            )
        if row.advertising > max(unit.profit, 0):
            issues.append(
                self._issue(
                    FinanceStatus.WARNING,
                    FinanceIssueType.ADS_ATE_PROFIT,
                    row.sku,
                    "advertising <= profit",
                    row.advertising,
                    round(row.advertising - max(unit.profit, 0), 2),
                    "Снизить ставки или остановить рекламу до проверки unit-экономики.",
                )
            )
        if row.commission <= 0:
            issues.append(
                self._issue(
                    FinanceStatus.WARNING,
                    FinanceIssueType.MISSING_COMMISSION,
                    row.sku,
                    "commission > 0",
                    row.commission,
                    row.commission,
                    "Загрузить комиссию маркетплейса перед финальным PnL.",
                )
            )
        if row.logistics <= 0:
            issues.append(
                self._issue(
                    FinanceStatus.WARNING,
                    FinanceIssueType.MISSING_LOGISTICS,
                    row.sku,
                    "logistics > 0",
                    row.logistics,
                    row.logistics,
                    "Загрузить логистику и возвратную логистику из отчета маркетплейса.",
                )
            )
        if unit.total_expenses > row.revenue:
            issues.append(
                self._issue(
                    FinanceStatus.CRITICAL,
                    FinanceIssueType.EXPENSES_OVER_REVENUE,
                    row.sku,
                    row.revenue,
                    unit.total_expenses,
                    round(unit.total_expenses - row.revenue, 2),
                    "Проверить расходы: сумма затрат больше выручки.",
                )
            )
        mismatch = round(row.report_profit - row.internal_profit, 2)
        if abs(mismatch) > 1:
            issues.append(
                self._issue(
                    FinanceStatus.WARNING,
                    FinanceIssueType.REPORT_INTERNAL_MISMATCH,
                    row.sku,
                    row.report_profit,
                    row.internal_profit,
                    mismatch,
                    "Сверить отчет маркетплейса с внутренней таблицей по SKU.",
                )
            )
        if row.previous_expenses > 0 and row.current_expenses > row.previous_expenses * 1.5:
            issues.append(
                self._issue(
                    FinanceStatus.WARNING,
                    FinanceIssueType.EXPENSE_SPIKE,
                    row.sku,
                    f"<= {round(row.previous_expenses * 1.5, 2)}",
                    row.current_expenses,
                    round(row.current_expenses - row.previous_expenses, 2),
                    "Разобрать скачок расходов по рекламе, логистике или штрафам.",
                )
            )
        if row.cost <= 0:
            issues.append(
                self._issue(
                    FinanceStatus.CRITICAL,
                    FinanceIssueType.MISSING_COST,
                    row.sku,
                    "cost > 0",
                    row.cost,
                    row.cost,
                    "Добавить себестоимость SKU до принятия решений по цене.",
                )
            )
        if row.taxes <= 0:
            issues.append(
                self._issue(
                    FinanceStatus.WARNING,
                    FinanceIssueType.MISSING_TAXES,
                    row.sku,
                    "taxes > 0",
                    row.taxes,
                    row.taxes,
                    "Посчитать налоги и обновить PnL перед финальным отчетом.",
                )
            )
        return issues

    @staticmethod
    def _issue(
        status: FinanceStatus,
        issue_type: FinanceIssueType,
        sku: str,
        expected: float | str | None,
        actual: float | str | None,
        difference: float | None,
        recommendation: str,
    ) -> FinanceIssue:
        return FinanceIssue(
            status=status,
            issue_type=issue_type,
            affected_sku=sku,
            expected_value=expected,
            actual_value=actual,
            difference=difference,
            recommendation=recommendation,
            needs_human_check=True,
            mock_mode=True,
        )
