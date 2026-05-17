from zentory.schemas.abc import (
    ABCAnalysisInput,
    ABCAnalysisReport,
    ABCAnalysisRow,
    ABCClass,
    ABCClassSummary,
    ABCMetric,
)


class ABCAnalysisService:
    def analyze(
        self, items: list[ABCAnalysisInput], metric: ABCMetric | str = ABCMetric.REVENUE
    ) -> ABCAnalysisReport:
        metric = ABCMetric(metric)
        sorted_items = sorted(
            items, key=lambda item: self._metric_value(item, metric), reverse=True
        )
        total_metric = sum(max(self._metric_value(item, metric), 0) for item in sorted_items)
        warnings: list[str] = []
        if total_metric == 0:
            warnings.append("ABC-анализ: total_metric=0, доли не могут быть рассчитаны")

        rows: list[ABCAnalysisRow] = []
        cumulative = 0.0
        for rank, item in enumerate(sorted_items, start=1):
            metric_value = max(self._metric_value(item, metric), 0)
            share = metric_value / total_metric if total_metric > 0 else 0.0
            cumulative += share
            cumulative_percent = round(cumulative * 100, 4) if total_metric > 0 else 0.0
            rows.append(
                ABCAnalysisRow(
                    sku=item.sku,
                    product_name=item.product_name,
                    metric_value=round(metric_value, 2),
                    share=round(share, 6),
                    cumulative_share=round(cumulative, 6) if total_metric > 0 else 0.0,
                    share_percent=round(share * 100, 4),
                    cumulative_share_percent=cumulative_percent,
                    abc_class=self._class_for(cumulative_percent),
                    rank=rank,
                    mock=True,
                )
            )

        return ABCAnalysisReport(
            metric=metric,
            total_metric=round(total_metric, 2),
            rows=rows,
            class_summary=self._class_summary(rows),
            warnings=warnings,
            mock_mode=True,
        )

    @staticmethod
    def _metric_value(item: ABCAnalysisInput, metric: ABCMetric) -> float:
        if metric == ABCMetric.REVENUE:
            return item.revenue
        if metric == ABCMetric.PROFIT:
            return item.profit
        return float(item.sales_qty)

    @staticmethod
    def _class_for(cumulative_percent: float) -> ABCClass:
        if cumulative_percent <= 80:
            return ABCClass.A
        if cumulative_percent <= 95:
            return ABCClass.B
        return ABCClass.C

    @staticmethod
    def _class_summary(rows: list[ABCAnalysisRow]) -> list[ABCClassSummary]:
        summaries: list[ABCClassSummary] = []
        for abc_class in ABCClass:
            class_rows = [row for row in rows if row.abc_class == abc_class]
            summaries.append(
                ABCClassSummary(
                    abc_class=abc_class,
                    sku_count=len(class_rows),
                    share_percent=round(sum(row.share_percent for row in class_rows), 4),
                )
            )
        return summaries
