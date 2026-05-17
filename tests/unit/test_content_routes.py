import asyncio

from zentory.api.routers.content import (
    content_brief,
    content_hypotheses,
    content_prompts,
    content_sku,
)
from zentory.services.content_ctr_service import ContentCTRService
from zentory.services.telegram_command_service import TelegramCommandService


def test_content_routes_return_mock_contracts() -> None:
    service = ContentCTRService()
    payload = {"sku": "ZNT-CONTENT-001"}

    brief = asyncio.run(content_brief(payload, service))
    hypotheses = asyncio.run(content_hypotheses(payload, service))
    prompts = asyncio.run(content_prompts(payload, service))
    sku = asyncio.run(content_sku("ZNT-CONTENT-001", service))

    assert brief["sku"] == "ZNT-CONTENT-001"
    assert hypotheses["mock_mode"] is True
    assert len(hypotheses["hypotheses"]) >= 5
    assert prompts["prompts"][0]["language"] == "en"
    assert prompts["prompts"][0]["russian_text_blocks"]
    assert sku["ctr_test_plan"]["publication_requires_approval"] is True
    assert sku["ctr_test_plan"]["bulk_change_requires_hard_approval"] is True


def test_content_ctr_telegram_commands_are_parsed() -> None:
    service = TelegramCommandService()

    content_sku = service.parse({"text": "/content_sku ZNT-CONTENT-001"})
    ctr_test = service.parse({"text": "/ctr_test"})
    content_brief = service.parse({"text": "/content_brief"})

    assert content_sku.event_type == "content_sku"
    assert content_sku.payload["sku"] == "ZNT-CONTENT-001"
    assert ctr_test.event_type == "ctr_test"
    assert content_brief.event_type == "content_brief"
