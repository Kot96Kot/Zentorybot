from zentory.schemas.seasonality import SeasonalityResult


class SeasonalityService:
    def __init__(
        self,
        coefficients: dict[str, dict[str, float] | float] | None = None,
        sku_coefficients: dict[str, dict[str, float]] | None = None,
    ) -> None:
        self.coefficients = coefficients or {
            "default": 1.0,
            "cosmetics": {
                "01": 0.9,
                "02": 1.0,
                "03": 1.1,
                "04": 1.05,
                "05": 1.0,
                "06": 0.95,
                "07": 0.9,
                "08": 1.0,
                "09": 1.1,
                "10": 1.15,
                "11": 1.25,
                "12": 1.35,
            },
        }
        self.sku_coefficients = sku_coefficients or {
            "ZNT-COS-001": {"11": 1.35, "12": 1.45},
        }

    def coefficient_for(self, *, category: str, month: int | str, sku: str | None = None) -> float:
        month_key = f"{int(month):02d}" if str(month).isdigit() else str(month)
        if sku is not None and sku in self.sku_coefficients:
            sku_months = self.sku_coefficients[sku]
            if month_key in sku_months:
                return sku_months[month_key]
        category_coefficients = self.coefficients.get(category)
        if isinstance(category_coefficients, dict):
            return category_coefficients.get(month_key, self.default_coefficient)
        if isinstance(category_coefficients, int | float):
            return float(category_coefficients)
        return self.default_coefficient

    def trend_coefficient(
        self, *, recent_avg_daily_sales: float, previous_avg_daily_sales: float
    ) -> float:
        if previous_avg_daily_sales <= 0:
            return 1.0 if recent_avg_daily_sales <= 0 else 1.5
        raw = recent_avg_daily_sales / previous_avg_daily_sales
        return min(1.5, max(0.7, round(raw, 4)))

    def build_result(
        self,
        *,
        category: str,
        month: int | str,
        sku: str | None = None,
        recent_avg_daily_sales: float = 0,
        previous_avg_daily_sales: float = 0,
    ) -> SeasonalityResult:
        return SeasonalityResult(
            sku=sku,
            category=category,
            month=f"{int(month):02d}" if str(month).isdigit() else str(month),
            seasonality_coefficient=self.coefficient_for(
                category=category, month=month, sku=sku
            ),
            trend_coefficient=self.trend_coefficient(
                recent_avg_daily_sales=recent_avg_daily_sales,
                previous_avg_daily_sales=previous_avg_daily_sales,
            ),
            mock_mode=True,
        )

    @property
    def default_coefficient(self) -> float:
        default = self.coefficients.get("default", 1.0)
        return float(default) if isinstance(default, int | float) else 1.0
