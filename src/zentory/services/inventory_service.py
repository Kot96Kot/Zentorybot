from datetime import date, timedelta

from zentory.schemas.inventory import (
    InventoryPriority,
    InventorySkuInput,
    InventorySkuReport,
    InventoryStatus,
    InventorySummary,
    ReplenishmentRecommendation,
    WarehouseStock,
)
from zentory.services.replenishment_service import ReplenishmentService


class InventoryService:
    def __init__(self, replenishment_service: ReplenishmentService | None = None) -> None:
        self.replenishment_service = replenishment_service or ReplenishmentService()

    def build_mock_items(self, sku: str | None = None) -> list[InventorySkuInput]:
        items = [
            InventorySkuInput(
                sku="ZNT-WB-001",
                total_stock=52,
                warehouse_stocks=[
                    WarehouseStock(
                        warehouse="Коледино", region="Центр", stock=0, is_key_warehouse=True
                    ),
                    WarehouseStock(warehouse="Казань", region="Поволжье", stock=52, in_transit=20),
                ],
                sales_7d=84,
                sales_14d=154,
                sales_30d=300,
                average_daily_sales=12,
                coverage_days=4.3,
                warehouse="Коледино",
                region="Центр",
                transit=20,
                supply_plan=60,
                minimum_stock=30,
                desired_stock_days=21,
                recent_daily_sales=[9, 10, 12, 13, 15],
                is_advertised=True,
            ),
            InventorySkuInput(
                sku="ZNT-OZON-002",
                total_stock=160,
                warehouse_stocks=[
                    WarehouseStock(
                        warehouse="Хоругвино", region="Центр", stock=90, is_key_warehouse=True
                    ),
                    WarehouseStock(warehouse="Санкт-Петербург", region="Северо-Запад", stock=70),
                ],
                sales_7d=84,
                sales_14d=170,
                sales_30d=340,
                average_daily_sales=12,
                coverage_days=13.3,
                warehouse="Хоругвино",
                region="Центр",
                transit=40,
                supply_plan=100,
                minimum_stock=40,
                desired_stock_days=25,
            ),
            InventorySkuInput(
                sku="ZNT-YM-003",
                total_stock=820,
                warehouse_stocks=[
                    WarehouseStock(
                        warehouse="Софьино", region="Центр", stock=520, is_key_warehouse=True
                    ),
                    WarehouseStock(warehouse="Екатеринбург", region="Урал", stock=300),
                ],
                sales_7d=0,
                sales_14d=0,
                sales_30d=8,
                average_daily_sales=0.2,
                coverage_days=4100,
                warehouse="Софьино",
                region="Центр",
                transit=0,
                supply_plan=0,
                minimum_stock=20,
                desired_stock_days=30,
                days_without_movement=52,
            ),
        ]
        if sku is None:
            return items
        return [item for item in items if item.sku == sku]

    def analyze_item(self, item: InventorySkuInput) -> InventorySkuReport:
        recommendations: list[ReplenishmentRecommendation] = []
        ads_alerts: list[str] = []
        status = self._status(item)
        priority = self._priority(item, status)
        stockout_date = self._stockout_date(item)
        telegram_alert = self._telegram_alert(item, status, stockout_date)

        if item.coverage_days < 14:
            recommendations.append(
                self.replenishment_service.shipping_recommendation(item, priority=priority)
            )
        for warehouse in item.warehouse_stocks:
            if item.average_daily_sales > 0 and warehouse.is_key_warehouse and warehouse.stock == 0:
                recommendations.append(
                    self.replenishment_service.redistribution_recommendation(item, warehouse)
                )
        slow_mover = item.days_without_movement > 45
        if slow_mover:
            recommendations.append(self.replenishment_service.slow_mover_recommendation(item))
        if item.is_advertised and item.coverage_days < 7:
            ads_alerts.append(
                "SKU в рекламе, но остатка меньше 7 дней: отправить alert в AdsAgent."
            )
        if self._sales_growing(item):
            if priority == InventoryPriority.HIGH:
                priority = InventoryPriority.CRITICAL
            elif priority not in {InventoryPriority.CRITICAL, InventoryPriority.HIGH}:
                priority = InventoryPriority.HIGH

        excess_stock = item.coverage_days > item.desired_stock_days * 2
        return InventorySkuReport(
            sku=item.sku,
            status=status,
            priority=priority,
            total_stock=item.total_stock,
            average_daily_sales=item.average_daily_sales,
            coverage_days=round(item.coverage_days, 1),
            stockout_date=stockout_date,
            out_of_stock_risk=item.coverage_days < 14,
            excess_stock=excess_stock,
            slow_mover=slow_mover,
            telegram_alert=telegram_alert,
            recommendations=recommendations,
            warehouse_stocks=item.warehouse_stocks,
            alerts_for_ads_agent=ads_alerts,
            mock=True,
        )

    def analyze(self, sku: str | None = None) -> InventorySummary:
        reports = [self.analyze_item(item) for item in self.build_mock_items(sku)]
        return InventorySummary(
            out_of_stock_risks=[report for report in reports if report.out_of_stock_risk],
            excess_skus=[report for report in reports if report.excess_stock],
            slow_movers=[report for report in reports if report.slow_mover],
            reports=reports,
            mock=True,
        )

    @staticmethod
    def _status(item: InventorySkuInput) -> InventoryStatus:
        if item.days_without_movement > 45:
            return InventoryStatus.SLOW_MOVER
        if item.coverage_days < 7:
            return InventoryStatus.CRITICAL
        if item.coverage_days < 14:
            return InventoryStatus.WARNING
        if item.coverage_days > item.desired_stock_days * 2:
            return InventoryStatus.EXCESS
        return InventoryStatus.OK

    @staticmethod
    def _priority(item: InventorySkuInput, status: InventoryStatus) -> InventoryPriority:
        if status == InventoryStatus.CRITICAL:
            return InventoryPriority.CRITICAL
        if status == InventoryStatus.WARNING:
            return InventoryPriority.HIGH
        if item.days_without_movement > 45:
            return InventoryPriority.MEDIUM
        return InventoryPriority.LOW

    @staticmethod
    def _stockout_date(item: InventorySkuInput) -> date | None:
        if item.average_daily_sales <= 0:
            return None
        return date.today() + timedelta(days=int(item.coverage_days))

    @staticmethod
    def _telegram_alert(
        item: InventorySkuInput, status: InventoryStatus, stockout_date: date | None
    ) -> str | None:
        if status == InventoryStatus.CRITICAL:
            return f"🚨 Critical OOS risk: {item.sku} закончится примерно {stockout_date}."
        if status == InventoryStatus.WARNING:
            return f"⚠️ Warning stock risk: {item.sku} покрытие меньше 14 дней."
        if status == InventoryStatus.SLOW_MOVER:
            return f"🐢 Slow mover: {item.sku} без движения больше 45 дней."
        return None

    @staticmethod
    def _sales_growing(item: InventorySkuInput) -> bool:
        if len(item.recent_daily_sales) < 3:
            return False
        last_three = item.recent_daily_sales[-3:]
        return last_three[0] < last_three[1] < last_three[2]
