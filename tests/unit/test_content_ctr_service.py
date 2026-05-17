from zentory.schemas.content_ctr import ContentRisk
from zentory.services.content_ctr_service import ContentCTRService


def test_content_ctr_service_builds_full_mock_factory_result() -> None:
    result = ContentCTRService().build_for_sku("ZNT-CONTENT-777")

    assert result.mock_mode is True
    assert result.brief.sku == "ZNT-CONTENT-777"
    assert result.brief.current_ctr < result.brief.target_ctr
    assert 5 <= len(result.hypotheses) <= 10
    assert result.prompts
    assert result.ctr_test_plan.publication_requires_approval is True
    assert result.ctr_test_plan.bulk_change_requires_hard_approval is True
    assert any("не публикуется автоматически" in note for note in result.safety_notes)


def test_hypotheses_include_required_main_photo_fields() -> None:
    service = ContentCTRService()
    brief = service.build_brief({"sku": "SKU-1"})

    hypotheses = service.generate_hypotheses(brief)

    first = hypotheses[0]
    assert first.idea
    assert first.why_it_may_work
    assert first.pain_addressed in brief.buyer_pains
    assert first.element_to_test
    assert first.risk in {ContentRisk.LOW, ContentRisk.MEDIUM, ContentRisk.HIGH}
    assert first.draft_only is True


def test_custom_brief_payload_is_preserved() -> None:
    brief = ContentCTRService().build_brief(
        {
            "marketplace": "ozon",
            "sku": "OZON-1",
            "product_name": "Органайзер",
            "category": "дом",
            "target_audience": "семьи",
            "buyer_pains": ["хаос на полке"],
            "key_features": ["3 секции"],
            "competitor_references": ["competitor hero photo"],
            "current_ctr": 1.2,
            "target_ctr": 2.1,
        }
    )

    assert brief.marketplace == "ozon"
    assert brief.sku == "OZON-1"
    assert brief.product_name == "Органайзер"
    assert brief.buyer_pains == ["хаос на полке"]
