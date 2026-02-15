from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional

from core.constants import (
    DEFAULT_INSTALLMENT_MONTHS,
    INSTALLMENT_MARKUP,
    AGE_FACTOR_PER_YEAR,
)

@dataclass
class Quote:
    company_id: int
    company_name: str
    company_logo_url: str
    wealth_level: int
    cash_price: int
    installment_total_price: int
    monthly_payment: int

class PricingService:
    @staticmethod
    def _current_year_fallback() -> int:
        return datetime.now().year

    @classmethod
    def calculate_quotes(
        cls,
        *,
        base_price_toman: float,
        production_year: int,
        rates: Iterable,
        installment_months: int = DEFAULT_INSTALLMENT_MONTHS,
        installment_markup: float = INSTALLMENT_MARKUP,
        current_year: Optional[int] = None,
    ) -> List[Quote]:
        if current_year is None:
            current_year = cls._current_year_fallback()

        age_years = max(0, current_year - production_year)
        age_factor = age_years * AGE_FACTOR_PER_YEAR

        quotes: List[Quote] = []
        for rate in rates:
            company = rate.company

            cash = (base_price_toman * (1 + age_factor)) * float(rate.car_value_coefficient) + float(rate.base_fee)
            cash_int = int(round(cash))

            installment_total = cash_int * (1 + installment_markup)
            installment_total_int = int(round(installment_total))
            monthly = int(round(installment_total_int / installment_months)) if installment_months else installment_total_int

            quotes.append(
                Quote(
                    company_id=company.id,
                    company_name=company.name,
                    company_logo_url=company.logo.url if getattr(company, "logo", None) else "",
                    wealth_level=getattr(company, "wealth_level", 0) or 0,
                    cash_price=cash_int,
                    installment_total_price=installment_total_int,
                    monthly_payment=monthly,
                )
            )
        return quotes
