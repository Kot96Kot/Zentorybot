from zentory.schemas.learning import (
    LearningActionApproval,
    LearningActionExecution,
    LearningActionProposed,
    LearningActionRecord,
    LearningActionStatus,
    LearningEvaluation,
    LearningSummary,
)


class LearningLoopService:
    def __init__(self) -> None:
        self._records: dict[str, LearningActionRecord] = {}

    def record_proposed(self, proposed: LearningActionProposed) -> LearningActionRecord:
        record = LearningActionRecord(
            action_id=proposed.action_id,
            agent=proposed.agent,
            sku=proposed.sku,
            recommendation=proposed.recommendation,
            expected_effect=proposed.expected_effect,
            metric_name=proposed.metric_name,
            metric_before=proposed.metric_before,
            proposed_at=proposed.proposed_at,
            metadata=proposed.metadata,
            conclusion="Действие предложено; результат еще не измерен.",
            status=LearningEvaluation.INCONCLUSIVE,
            mock_mode=True,
        )
        self._records[record.action_id] = record
        return record

    def record_approved(
        self, action_id: str, approval: LearningActionApproval
    ) -> LearningActionRecord:
        record = self._ensure_record(action_id)
        record.approved_by = approval.approved_by
        record.approved_at = approval.approved_at
        record.conclusion = "Действие подтверждено; ждем выполнения и метрик после проверки."
        self._records[action_id] = record
        return record

    def record_executed(
        self, action_id: str, execution: LearningActionExecution
    ) -> LearningActionRecord:
        record = self._ensure_record(action_id)
        record.executed_at = execution.executed_at
        record.execution_status = execution.execution_status
        if execution.execution_status == LearningActionStatus.FAILED:
            record.status = LearningEvaluation.FAILED
            record.action_success = False
            record.success_score = 0.0
            record.conclusion = "Действие не выполнено, поэтому правило нельзя усиливать."
        else:
            record.conclusion = "Действие выполнено; успех будет оценен только после метрик."
        self._records[action_id] = record
        return record

    def record_metric_after(
        self, action_id: str, metric_after: float | None
    ) -> LearningActionRecord:
        record = self._ensure_record(action_id)
        record.metric_after = metric_after
        self._evaluate(record)
        self._records[action_id] = record
        return record

    def list_actions(self) -> list[LearningActionRecord]:
        return sorted(self._records.values(), key=lambda item: item.proposed_at, reverse=True)

    def get_by_sku(self, sku: str) -> list[LearningActionRecord]:
        return [record for record in self.list_actions() if record.sku == sku]

    def summary(self, records: list[LearningActionRecord] | None = None) -> LearningSummary:
        items = records if records is not None else self.list_actions()
        return LearningSummary(
            total_actions=len(items),
            successful_actions=sum(
                1 for item in items if item.status == LearningEvaluation.SUCCESS
            ),
            partial_success_actions=sum(
                1 for item in items if item.status == LearningEvaluation.PARTIAL_SUCCESS
            ),
            failed_actions=sum(1 for item in items if item.status == LearningEvaluation.FAILED),
            inconclusive_actions=sum(
                1 for item in items if item.status == LearningEvaluation.INCONCLUSIVE
            ),
            strengthen_rules=[
                item.recommendation for item in items if item.status == LearningEvaluation.SUCCESS
            ],
            mock_mode=True,
        )

    def _ensure_record(self, action_id: str) -> LearningActionRecord:
        try:
            return self._records[action_id]
        except KeyError as exc:
            raise KeyError(f"Learning action {action_id} not found") from exc

    def _evaluate(self, record: LearningActionRecord) -> None:
        if record.metric_after is None:
            record.effect = None
            record.success_score = None
            record.action_success = False
            record.status = LearningEvaluation.INCONCLUSIVE
            record.conclusion = "Нет метрик после действия: бот не считает действие успешным."
            return

        effect = round(record.metric_before - record.metric_after, 4)
        if not self._lower_is_better(record):
            effect = round(record.metric_after - record.metric_before, 4)
        denominator = abs(record.metric_before) if record.metric_before != 0 else 1.0
        score = round(effect / denominator, 4)
        record.effect = effect
        record.success_score = score
        record.action_success = score > 0

        if score >= 0.15:
            record.status = LearningEvaluation.SUCCESS
            record.conclusion = (
                "Метрика улучшилась существенно: "
                "action_success=true, правило можно усиливать."
            )
        elif score > 0:
            record.status = LearningEvaluation.PARTIAL_SUCCESS
            record.conclusion = (
                "Метрика улучшилась частично: "
                "правило можно оставить под наблюдением."
            )
        else:
            record.status = LearningEvaluation.FAILED
            record.conclusion = (
                "Метрика не улучшилась: "
                "правило нельзя усиливать без ручной проверки."
            )

    @staticmethod
    def _lower_is_better(record: LearningActionRecord) -> bool:
        metric_text = record.metric_name.lower()
        text = f"{record.metric_name} {record.expected_effect} {record.recommendation}".lower()
        lower_markers = (
            "drr",
            "дрр",
            "acos",
            "cost",
            "расход",
            "сниз",
            "уменьш",
            "lower",
            "reduce",
        )
        higher_markers = (
            "orders",
            "заказ",
            "revenue",
            "выруч",
            "увелич",
            "рост",
            "raise",
            "increase",
        )
        if any(marker in metric_text for marker in higher_markers):
            return False
        if any(marker in metric_text for marker in lower_markers):
            return True
        if any(marker in text for marker in lower_markers):
            return True
        if any(marker in text for marker in higher_markers):
            return False
        return True
