from pathlib import Path

from zentory.integrations.telegram.commands import SUPPORTED_COMMANDS

REQUIRED_PATHS = (
    "docs/platform_algorithm.md",
    "docs/platform_principles.md",
    "docs/automation_filter.md",
    "docs/action_lifecycle.md",
    "docs/safety_modes.md",
    "docs/data_contracts.md",
    "docs/forecast_abc_module.md",
    "docs/supply_localization_planner.md",
    "docs/content_ctr_factory.md",
    "docs/finance_checker.md",
    "docs/learning_loop.md",
    "docs/mvp_demo_checklist.md",
    "src/zentory/agents/forecast_abc_agent.py",
    "src/zentory/agents/supply_agent.py",
    "src/zentory/agents/content_ctr_agent.py",
    "src/zentory/agents/finance_checker_agent.py",
    "src/zentory/agents/sku_agent.py",
    "src/zentory/services/forecast_service.py",
    "src/zentory/services/abc_analysis_service.py",
    "src/zentory/services/stock_forecast_service.py",
    "src/zentory/services/calculation_self_check_service.py",
    "src/zentory/services/seasonality_service.py",
    "src/zentory/services/supply_planner_service.py",
    "src/zentory/services/localization_service.py",
    "src/zentory/services/content_ctr_service.py",
    "src/zentory/services/content_reference_service.py",
    "src/zentory/services/prompt_generation_service.py",
    "src/zentory/services/finance_checker_service.py",
    "src/zentory/services/pnl_check_service.py",
    "src/zentory/services/dds_check_service.py",
    "src/zentory/services/unit_profit_service.py",
    "src/zentory/services/learning_loop_service.py",
    "src/zentory/services/action_result_service.py",
    "src/zentory/services/data_normalization_service.py",
    "src/zentory/schemas/marketplace.py",
    "src/zentory/schemas/sku.py",
    "src/zentory/schemas/sales.py",
    "src/zentory/schemas/stocks.py",
    "src/zentory/schemas/ads.py",
    "src/zentory/schemas/reviews.py",
    "src/zentory/schemas/unit_economics.py",
    "src/zentory/schemas/forecast.py",
    "src/zentory/schemas/abc.py",
    "src/zentory/schemas/seasonality.py",
    "src/zentory/schemas/supply.py",
    "src/zentory/schemas/content_ctr.py",
    "src/zentory/schemas/finance.py",
    "src/zentory/schemas/learning.py",
    "src/zentory/schemas/sku_intelligence.py",
    "src/zentory/api/routers/analytics.py",
    "src/zentory/api/routers/supply.py",
    "src/zentory/api/routers/content.py",
    "src/zentory/api/routers/finance.py",
    "src/zentory/api/routers/learning.py",
    "src/zentory/api/routers/sku.py",
)

REQUIRED_MANAGEMENT_COMMANDS = {
    "/daily",
    "/alerts",
    "/sku",
    "/plan",
    "/approve",
    "/reject",
    "/rollback",
    "/status",
    "/abc",
    "/forecast",
    "/stock_risks",
    "/content_sku",
    "/finance_check",
}


def test_pr3_required_modules_are_preserved_after_merge() -> None:
    missing = [path for path in REQUIRED_PATHS if not Path(path).is_file()]

    assert missing == []


def test_no_merge_conflict_markers_remain() -> None:
    markers = ("<" * 7, "=" * 7, ">" * 7)
    text_files = [
        *Path("src").rglob("*.py"),
        *Path("tests").rglob("*.py"),
        *Path("docs").rglob("*.md"),
        Path("README.md"),
    ]

    offenders = [
        str(path)
        for path in text_files
        if any(marker in path.read_text(encoding="utf-8") for marker in markers)
    ]

    assert offenders == []


def test_telegram_management_commands_remain_available() -> None:
    assert REQUIRED_MANAGEMENT_COMMANDS.issubset(set(SUPPORTED_COMMANDS))
