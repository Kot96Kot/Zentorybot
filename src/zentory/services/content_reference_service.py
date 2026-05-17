from zentory.schemas.content_ctr import ContentBriefCTR


class ContentReferenceService:
    def build_mock_brief(self, sku: str | None = None) -> ContentBriefCTR:
        normalized_sku = sku or "ZNT-CONTENT-001"
        return ContentBriefCTR(
            marketplace="wildberries",
            sku=normalized_sku,
            product_name="Вакууматор для продуктов Zentory Home",
            category="кухонная техника",
            target_audience="семьи, которые готовят заранее и хотят дольше хранить продукты",
            buyer_pains=[
                "продукты быстро портятся",
                "не хватает места в морозилке",
                "покупатель не понимает выгоду вакуума с первого фото",
            ],
            key_features=[
                "режим для сухих и влажных продуктов",
                "ширина пакета до 30 см",
                "компактное хранение",
                "быстрая запайка без сложных настроек",
            ],
            competitor_references=[
                "Kitfort: крупный товар на белом фоне",
                "Redmond: инфографика с режимами",
                "Xiaomi: минималистичный lifestyle",
            ],
            current_ctr=1.8,
            target_ctr=2.6,
            mock_mode=True,
        )

    def brief_from_payload(self, payload: dict[str, object] | None = None) -> ContentBriefCTR:
        payload = payload or {}
        if payload.get("product_name"):
            return ContentBriefCTR(
                marketplace=str(payload.get("marketplace", "wildberries")),
                sku=str(payload.get("sku", "ZNT-CONTENT-001")),
                product_name=str(payload["product_name"]),
                category=str(payload.get("category", "товары для дома")),
                target_audience=str(payload.get("target_audience", "покупатели маркетплейса")),
                buyer_pains=list(payload.get("buyer_pains", [])),
                key_features=list(payload.get("key_features", [])),
                competitor_references=list(payload.get("competitor_references", [])),
                current_ctr=float(payload.get("current_ctr", 1.5)),
                target_ctr=float(payload.get("target_ctr", 2.3)),
                mock_mode=True,
            )
        sku = str(payload.get("sku")) if payload.get("sku") else None
        return self.build_mock_brief(sku)
