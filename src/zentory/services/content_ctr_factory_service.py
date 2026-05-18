from zentory.schemas.platform_modules import ContentCTRExperiment, ContentCTRFactoryReport


class ContentCTRFactoryService:
    def build_report(self) -> ContentCTRFactoryReport:
        return ContentCTRFactoryReport(
            experiments=[
                ContentCTRExperiment(
                    sku="WB-MOCK-1",
                    current_ctr_percent=1.8,
                    target_ctr_percent=2.5,
                    hypothesis="Первый экран не объясняет размерную сетку и снижает клики.",
                    title_variant="Базовая футболка Zentory, плотный хлопок, размер в размер",
                    first_screen_variant=(
                        "Добавить бейджи: плотность, размерная сетка, быстрый возврат."
                    ),
                    safety_note=(
                        "Контент только предлагается; публикация требует "
                        "Action Center approval."
                    ),
                )
            ]
        )
