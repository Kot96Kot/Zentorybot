from zentory.schemas.platform_modules import LearningLoopReport, LearningLoopSignal


class LearningLoopService:
    def build_report(self) -> LearningLoopReport:
        return LearningLoopReport(
            signals=[
                LearningLoopSignal(
                    source_module="content_ctr_factory",
                    metric="ctr_percent",
                    before=1.8,
                    after=2.3,
                    insight="Карточки с явной размерной сеткой получают больше кликов.",
                    next_rule_update="Для одежды добавлять size-proof блок в первые изображения.",
                ),
                LearningLoopSignal(
                    source_module="supply_localization",
                    metric="coverage_days",
                    before=5.0,
                    after=18.5,
                    insight="Перелокация A SKU снижает срочность ручных поставок.",
                    next_rule_update=(
                        "Поднимать приоритет локализации для ABC A "
                        "при покрытии < 7 дней."
                    ),
                ),
            ]
        )
