from django.conf import settings
from django.db import models

from apps.docs.models import Docs, Price


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="Пользователь"
    )
    docs = models.ForeignKey(
        Docs, on_delete=models.CASCADE, help_text="Документ для анализа"
    )
    order_price = models.FloatField(default=0.0)
    payment = models.BooleanField(default=False, help_text="Оплачен ли заказ")

    def calculate_price(self):
        """Вычисляет цену на основе размера документа и типа."""
        price = Price.objects.filter(
            file_type=self.docs.file.name.split(".")[-1]
        ).first()
        if price:
            self.order_price = self.docs.size * price.price
            self.save()

    def __str__(self):
        return f"Cart {self.id} - User {self.user.username} - Price {self.order_price} руб."
