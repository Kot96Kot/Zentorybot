from zentory.schemas.finance import DDSCheckResult, FinanceIssue, FinanceIssueType, FinanceStatus


class DDSCheckService:
    def check(
        self,
        *,
        cash_in: float,
        cash_out: float,
        opening_cash: float,
        actual_closing_cash: float,
        tolerance: float = 1.0,
    ) -> DDSCheckResult:
        expected = round(opening_cash + cash_in - cash_out, 2)
        difference = round(actual_closing_cash - expected, 2)
        issues: list[FinanceIssue] = []
        status = FinanceStatus.OK
        if abs(difference) > tolerance:
            status = FinanceStatus.WARNING
            issues.append(
                FinanceIssue(
                    status=FinanceStatus.WARNING,
                    issue_type=FinanceIssueType.CASH_FLOW_MISMATCH,
                    affected_sku="ALL",
                    expected_value=expected,
                    actual_value=actual_closing_cash,
                    difference=difference,
                    recommendation=(
                        "Сверить DDS: банк, удержания маркетплейса "
                        "и внутреннюю таблицу."
                    ),
                    needs_human_check=True,
                    mock_mode=True,
                )
            )
        return DDSCheckResult(
            status=status,
            issues=issues,
            cash_in=round(cash_in, 2),
            cash_out=round(cash_out, 2),
            expected_closing_cash=expected,
            actual_closing_cash=round(actual_closing_cash, 2),
            difference=difference,
            mock_mode=True,
        )
