from django.conf import settings
from django.db import models

from apps.docs.models import Docs


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
        # Временный словарь с ценами
        PRICE_MAP = {
            "jpg": 0.05,
            "jpeg": 0.05,
            "png": 0.07,
            "pdf": 0.10,
        }

        # Получаем расширение файла
        file_extension = self.docs.file.name.split(".")[-1].lower()

        # Получаем цену из временного словаря
        price_per_kb = PRICE_MAP.get(file_extension)

        if price_per_kb is None:
            # Если расширение не поддерживается
            raise ValueError(f"Цена для типа файла '{file_extension}' не задана.")

        # Рассчитываем цену
        self.order_price = self.docs.size * price_per_kb
        self.save()

    def __str__(self):
        return f"Cart {self.id} - User {self.user.username} - Price {self.order_price} руб."
