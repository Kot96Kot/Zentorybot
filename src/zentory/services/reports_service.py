from typing import Any


class ReportsService:
    async def daily_report(self) -> dict[str, Any]:
        return {
            "mock": True,
            "title": "Ежедневный mock-отчет Zentorybot",
            "sales": {"orders": 6, "revenue": 12540},
            "alerts": ["mock: проверить остатки SKU WB-MOCK-1"],
        }
