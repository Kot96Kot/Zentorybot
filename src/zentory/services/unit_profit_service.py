from zentory.schemas.finance import FinanceSkuInput, FinanceStatus, UnitFinanceResult
from zentory.schemas.promo import PromoSkuInput, UnitProfitBreakdown


class UnitProfitService:

    def calculate_finance(self, item: FinanceSkuInput) -> UnitFinanceResult:
        total_expenses = (
            item.commission
            + item.logistics
            + item.acquiring
            + item.advertising
            + item.cost
            + item.storage
            + item.penalties
            + item.return_logistics
            + item.taxes
        )
        profit = item.revenue - total_expenses
        margin_percent = profit / item.revenue if item.revenue > 0 else -1
        status = FinanceStatus.OK
        if profit < 0 or total_expenses > item.revenue or item.price < item.minimum_price:
            status = FinanceStatus.CRITICAL
        elif item.commission <= 0 or item.logistics <= 0 or item.taxes <= 0:
            status = FinanceStatus.WARNING
        return UnitFinanceResult(
            sku=item.sku,
            revenue=round(item.revenue, 2),
            commission=round(item.commission, 2),
            logistics=round(item.logistics, 2),
            acquiring=round(item.acquiring, 2),
            advertising=round(item.advertising, 2),
            cost=round(item.cost, 2),
            storage=round(item.storage, 2),
            penalties=round(item.penalties, 2),
            return_logistics=round(item.return_logistics, 2),
            taxes=round(item.taxes, 2),
            total_expenses=round(total_expenses, 2),
            profit=round(profit, 2),
            margin_percent=round(margin_percent, 4),
            minimum_price=round(item.minimum_price, 2),
            price=round(item.price, 2),
            status=status,
            mock_mode=True,
        )

    def calculate(self, item: PromoSkuInput) -> UnitProfitBreakdown:
        revenue = item.promo_price
        commission = revenue * item.commission_percent
        acquiring = revenue * item.acquiring_percent
        taxes = revenue * item.tax_percent
        mandatory_costs = (
            item.cost_price
            + item.logistics_cost
            + commission
            + acquiring
            + taxes
            + item.storage_cost_per_unit
            + item.return_logistics_per_unit
        )
        profit = (
            revenue
            - commission
            - item.logistics_cost
            - acquiring
            - item.advertising_cost_per_unit
            - item.cost_price
            - item.storage_cost_per_unit
            - item.penalties_per_unit
            - item.return_logistics_per_unit
            - taxes
        )
        margin_percent = profit / revenue if revenue > 0 else -1
        return UnitProfitBreakdown(
            revenue=round(revenue, 2),
            commission=round(commission, 2),
            logistics=round(item.logistics_cost, 2),
            acquiring=round(acquiring, 2),
            advertising=round(item.advertising_cost_per_unit, 2),
            cost_price=round(item.cost_price, 2),
            storage=round(item.storage_cost_per_unit, 2),
            penalties=round(item.penalties_per_unit, 2),
            return_logistics=round(item.return_logistics_per_unit, 2),
            taxes=round(taxes, 2),
            profit=round(profit, 2),
            margin_percent=round(margin_percent, 4),
            mandatory_costs=round(mandatory_costs, 2),
            mock=True,
        )

    def minimum_price(self, item: PromoSkuInput) -> float:
        variable_percent = item.commission_percent + item.acquiring_percent + item.tax_percent
        fixed_costs = (
            item.cost_price
            + item.logistics_cost
            + item.advertising_cost_per_unit
            + item.storage_cost_per_unit
            + item.penalties_per_unit
            + item.return_logistics_per_unit
        )
        denominator = max(1 - variable_percent - item.minimum_margin_percent, 0.01)
        return round(fixed_costs / denominator, 2)
