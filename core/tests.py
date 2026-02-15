from django.test import TestCase
from core.services.pricing_service import PricingService
from core.models import User, InsuranceCard, Order, Installment
from core.services.order_service import OrderService


class SimpleTest(TestCase):
    def test_basic(self):
        self.assertEqual(1, 1)


class PricingServiceTest(TestCase):
    def test_calculate_quotes_returns_positive_prices(self):
        class FakeCompany:
            id = 1
            name = "TestCo"
            wealth_level = 1
            logo = None

        class FakeRate:
            company = FakeCompany()
            car_value_coefficient = 1.1
            base_fee = 1000000

        quotes = PricingService.calculate_quotes(
            base_price_toman=500_000_000,
            production_year=2022,
            rates=[FakeRate()],
            current_year=2024,
        )

        self.assertEqual(len(quotes), 1)
        self.assertTrue(quotes[0].cash_price > 0)
        self.assertTrue(quotes[0].monthly_payment > 0)

class OrderServiceTest(TestCase):
    def test_generate_installments_creates_rows(self):
        user = User.objects.create_user(mobile="09120000000", password="12345678")
        insurance = InsuranceCard.objects.create(title="Test", slug="test", insurance_type="third_party")
        order = Order.objects.create(user=user, insurance=insurance, price=6000000, payment_type="installment")

        OrderService.generate_installments(order, 6)

        self.assertEqual(Installment.objects.filter(order=order).count(), 6)
