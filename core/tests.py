from django.test import TestCase
from core.services.pricing_service import PricingService
from core.models import User, InsuranceCard, Order, Installment
from core.services.order_service import OrderService
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

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
        


User = get_user_model()

class OrderServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(mobile="09120000000", password="12345678")
        self.insurance = InsuranceCard.objects.create(
            title="Test Insurance",
            slug="test-insurance",
            insurance_type="third_party",
        )

    def test_generate_installments_creates_correct_count(self):
        order = Order.objects.create(user=self.user, insurance=self.insurance, price=6_000_000)
        OrderService.generate_installments(order, count=6)
        self.assertEqual(Installment.objects.filter(order=order).count(), 6)

    def test_installments_amount_sum_is_close_to_order_price(self):
        order = Order.objects.create(user=self.user, insurance=self.insurance, price=6_000_000)
        OrderService.generate_installments(order, count=6)
        total = sum(i.amount for i in Installment.objects.filter(order=order))
        self.assertAlmostEqual(total, order.price, delta=1)

    def test_installments_due_dates_are_increasing(self):
        order = Order.objects.create(user=self.user, insurance=self.insurance, price=6_000_000)
        OrderService.generate_installments(order, count=3)
        dues = list(Installment.objects.filter(order=order).order_by("due_date").values_list("due_date", flat=True))
        self.assertTrue(dues[0] < dues[1] < dues[2])

class PricingApiTests(TestCase):
    def test_calculate_prices_requires_model_id(self):
        url = reverse("core:calculate_prices_api")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 400)
