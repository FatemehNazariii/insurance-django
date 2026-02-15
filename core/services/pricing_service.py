class PricingService:
    @staticmethod
    def calculate_price(base_price, year, rate):
        from datetime import datetime
        current_year = datetime.now().year
        age_factor = (current_year - year) * 0.01
        
        final_price = (
            (base_price * (1 + age_factor))
            * rate.car_value_coefficient
            + rate.base_fee
        )
        return final_price
