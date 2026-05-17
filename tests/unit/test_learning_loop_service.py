from zentory.schemas.learning import (
    LearningActionApproval,
    LearningActionExecution,
    LearningActionProposed,
    LearningEvaluation,
)
from zentory.services.learning_loop_service import LearningLoopService


def test_learning_loop_marks_success_when_after_metric_improves() -> None:
    service = LearningLoopService()

    service.record_proposed(
        LearningActionProposed(
            action_id="act-1",
            agent="ads_agent",
            sku="SKU-DRR",
            recommendation="снизить ставку на 15%",
            expected_effect="снизить ДРР без просадки заказов",
            metric_name="ДРР",
            metric_before=18.0,
        )
    )
    service.record_approved("act-1", LearningActionApproval(approved_by="manager"))
    service.record_executed("act-1", LearningActionExecution())
    result = service.record_metric_after("act-1", 12.0)

    assert result.status == LearningEvaluation.SUCCESS
    assert result.action_success is True
    assert result.effect == 6.0
    assert result.success_score == 0.3333
    assert "правило можно усиливать" in result.conclusion


def test_learning_loop_is_inconclusive_without_after_metric() -> None:
    service = LearningLoopService()

    service.record_proposed(
        LearningActionProposed(
            action_id="act-2",
            agent="pricing_agent",
            sku="SKU-NO-DATA",
            recommendation="снизить цену",
            expected_effect="снизить ДРР",
            metric_before=18.0,
        )
    )
    result = service.record_metric_after("act-2", None)

    assert result.status == LearningEvaluation.INCONCLUSIVE
    assert result.action_success is False
    assert result.success_score is None
    assert "не считает действие успешным" in result.conclusion


def test_learning_loop_filters_by_sku_and_builds_summary() -> None:
    service = LearningLoopService()
    service.record_proposed(
        LearningActionProposed(
            action_id="act-3",
            agent="ads_agent",
            sku="SKU-1",
            recommendation="снизить ставку",
            expected_effect="снизить ДРР",
            metric_before=20.0,
        )
    )
    service.record_metric_after("act-3", 19.0)
    service.record_proposed(
        LearningActionProposed(
            action_id="act-4",
            agent="ads_agent",
            sku="SKU-2",
            recommendation="снизить ставку",
            expected_effect="снизить ДРР",
            metric_before=20.0,
        )
    )
    service.record_metric_after("act-4", 25.0)

    sku_records = service.get_by_sku("SKU-1")
    summary = service.summary()

    assert [record.action_id for record in sku_records] == ["act-3"]
    assert summary.total_actions == 2
    assert summary.partial_success_actions == 1
    assert summary.failed_actions == 1
