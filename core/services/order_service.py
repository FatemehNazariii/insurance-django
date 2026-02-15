from datetime import timedelta
from django.utils import timezone

class OrderService:
    @staticmethod
    def generate_installments(order, count: int, days_step: int = 30):
        from core.models import Installment

        if count <= 0:
            return

        amount = order.price / count
        for i in range(count):
            Installment.objects.create(
                order=order,
                amount=amount,
                due_date=timezone.now().date() + timedelta(days=days_step * (i + 1)),
                is_paid=False,
            )
