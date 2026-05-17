from zentory.schemas.learning import ActionResultRequest, LearningEvaluation
from zentory.services.action_result_service import ActionResultService


def test_action_result_service_records_full_lifecycle_success() -> None:
    service = ActionResultService()

    result = service.record_action_result(
        ActionResultRequest(
            action_id="act-result-1",
            agent="ads_agent",
            sku="SKU-DRR",
            recommendation="снизить ставку на 15%",
            expected_effect="ДРР снизится, заказы не просядут",
            metric_name="ДРР",
            metric_before=18.0,
            metric_after=12.0,
            approved_by="cfo",
        )
    )

    assert result.status == LearningEvaluation.SUCCESS
    assert result.approved_by == "cfo"
    assert result.executed_at is not None
    assert result.mock_mode is True
    assert service.summary().successful_actions == 1


def test_action_result_service_does_not_claim_success_without_metrics() -> None:
    service = ActionResultService()

    result = service.record_action_result(
        ActionResultRequest(
            action_id="act-result-2",
            agent="ads_agent",
            sku="SKU-NO-AFTER",
            recommendation="снизить ставку на 15%",
            expected_effect="снизить ДРР",
            metric_before=18.0,
            metric_after=None,
        )
    )

    assert result.status == LearningEvaluation.INCONCLUSIVE
    assert result.action_success is False
    assert service.summary().inconclusive_actions == 1
