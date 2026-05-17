from zentory.schemas.seasonality import SeasonalityResult


class SeasonalityService:
    def __init__(
        self,
        category_coefficients: dict[str, float] | None = None,
        month_coefficients: dict[str, float] | None = None,
        sku_coefficients: dict[str, dict[str, float] | float] | None = None,
        coefficients: dict[str, dict[str, float] | float] | None = None,
    ) -> None:
        legacy_months = coefficients or {}
        self.category_coefficients = category_coefficients or {
            "default": 1.0,
            "cosmetics": 1.0,
            "home": 0.95,
            "accessories": 0.9,
        }
        self.month_coefficients = month_coefficients or {
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
        }
        self.sku_coefficients = sku_coefficients or {
            "ZNT-COS-001": {"11": 1.08, "12": 1.0741},
        }
        self.legacy_months = legacy_months

    def coefficient_for(self, *, category: str, month: int | str, sku: str | None = None) -> float:
        if category not in self.category_coefficients and category not in self.legacy_months:
            return self.default_coefficient
        return self.seasonality_coefficient_for(category=category, month=month, sku=sku)

    def category_coefficient_for(self, category: str) -> float:
        return float(
            self.category_coefficients.get(category, self.category_coefficients.get("default", 1.0))
        )

    def month_coefficient_for(self, month: int | str) -> float:
        month_key = self._month_key(month)
        return float(self.month_coefficients.get(month_key, 1.0))

    def sku_coefficient_for(self, *, sku: str | None, month: int | str) -> float:
        if sku is None:
            return 1.0
        coefficient = self.sku_coefficients.get(sku)
        if isinstance(coefficient, dict):
            return float(coefficient.get(self._month_key(month), 1.0))
        if isinstance(coefficient, int | float):
            return float(coefficient)
        return 1.0

    def seasonality_coefficient_for(
        self, *, category: str, month: int | str, sku: str | None = None
    ) -> float:
        # Preserve compatibility with the earlier category->month coefficient map when injected.
        month_key = self._month_key(month)
        legacy_category = self.legacy_months.get(category)
        if isinstance(legacy_category, dict) and sku is None:
            return float(legacy_category.get(month_key, self.default_coefficient))
        if isinstance(legacy_category, int | float) and sku is None:
            return float(legacy_category)
        return round(
            self.category_coefficient_for(category)
            * self.month_coefficient_for(month)
            * self.sku_coefficient_for(sku=sku, month=month),
            4,
        )

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
            month=self._month_key(month),
            category_coefficient=self.category_coefficient_for(category),
            month_coefficient=self.month_coefficient_for(month),
            sku_coefficient=self.sku_coefficient_for(sku=sku, month=month),
            seasonality_coefficient=self.seasonality_coefficient_for(
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
        legacy_default = self.legacy_months.get("default")
        if isinstance(legacy_default, int | float):
            return float(legacy_default)
        return float(self.category_coefficients.get("default", 1.0))

    @staticmethod
    def _month_key(month: int | str) -> str:
        return f"{int(month):02d}" if str(month).isdigit() else str(month)
