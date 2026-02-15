class OrderService:
    @staticmethod
    def create_installments(order, count):
        from datetime import timedelta
        from django.utils import timezone
        
        for i in range(count):
            Installment.objects.create(
                order=order,
                amount=order.price / count,
                due_date=timezone.now() + timedelta(days=30 * (i + 1))
            )
