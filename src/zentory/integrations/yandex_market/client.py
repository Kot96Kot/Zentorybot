from typing import Any


class YandexMarketClient:
    marketplace = "yandex_market"

    async def fetch_orders(self) -> list[dict[str, Any]]:
        return [{"mock": True, "marketplace": self.marketplace, "orders": 1}]

    async def fetch_stocks(self) -> list[dict[str, Any]]:
        return [{"mock": True, "sku": "YM-MOCK-1", "stock": 18}]

    async def fetch_prices(self) -> list[dict[str, Any]]:
        return [{"mock": True, "sku": "YM-MOCK-1", "price": 2190}]

    async def fetch_reviews(self) -> list[dict[str, Any]]:
        return [{"mock": True, "rating": 5, "text": "mock review"}]

    async def fetch_questions(self) -> list[dict[str, Any]]:
        return [{"mock": True, "question": "mock question"}]

    async def fetch_ads_stats(self) -> list[dict[str, Any]]:
        return [{"mock": True, "drr": 0.11, "ctr": 0.05}]

    async def update_price(self, sku: str, price: int) -> dict[str, Any]:
        return {"mock": True, "sku": sku, "price": price, "status": "not_sent"}

    async def send_reply(self, review_id: str, text: str) -> dict[str, Any]:
        return {"mock": True, "review_id": review_id, "text": text, "status": "not_sent"}
