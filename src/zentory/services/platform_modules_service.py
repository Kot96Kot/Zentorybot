from zentory.schemas.platform_modules import PlatformModulesSnapshot
from zentory.services.content_ctr_factory_service import ContentCTRFactoryService
from zentory.services.data_contracts_service import DataContractsService
from zentory.services.finance_checker_service import FinanceCheckerService
from zentory.services.forecast_abc_service import ForecastABCService
from zentory.services.learning_loop_service import LearningLoopService
from zentory.services.supply_localization_service import SupplyLocalizationService


class PlatformModulesService:
    def __init__(
        self,
        forecast_abc: ForecastABCService | None = None,
        supply: SupplyLocalizationService | None = None,
        content_ctr: ContentCTRFactoryService | None = None,
        finance: FinanceCheckerService | None = None,
        learning_loop: LearningLoopService | None = None,
        data_contracts: DataContractsService | None = None,
    ) -> None:
        self.forecast_abc = forecast_abc or ForecastABCService()
        self.supply = supply or SupplyLocalizationService()
        self.content_ctr = content_ctr or ContentCTRFactoryService()
        self.finance = finance or FinanceCheckerService()
        self.learning_loop = learning_loop or LearningLoopService()
        self.data_contracts = data_contracts or DataContractsService()

    def build_snapshot(self) -> PlatformModulesSnapshot:
        return PlatformModulesSnapshot(
            forecast_abc=self.forecast_abc.build_report(),
            supply_localization=self.supply.build_plan(),
            content_ctr_factory=self.content_ctr.build_report(),
            finance_checker=self.finance.build_report(),
            learning_loop=self.learning_loop.build_report(),
            data_contracts=self.data_contracts.build_report(),
        )
