from django.conf import settings
from django.db import models

from apps.docs.models import Docs, Price


class Cart(models.Model):
    user: settings.AUTH_USER_MODEL = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="Пользователь"
    )
    docs: Docs = models.ForeignKey(
        Docs, on_delete=models.CASCADE, help_text="Документ для анализа"
    )
    order_price: float = models.FloatField(default=0.0)
    payment: bool = models.BooleanField(default=False, help_text="Оплачен ли заказ")

    def calculate_price(self) -> None:
        """
        Вычисляет цену на основе размера документа и типа.

        :raises ValueError: Если цена для указанного типа файла не задана.
        """
        # Получаем расширение файла
        file_extension: str = self.docs.file.name.split(".")[-1].lower()

        try:
            # Получаем цену из модели Price
            price_entry: Price = Price.objects.get(file_type=file_extension)
            price_per_kb: float = price_entry.price
        except Price.DoesNotExist:
            # Если расширение не поддерживается
            raise ValueError(f"Цена для типа файла '{file_extension}' не задана.")

        # Рассчитываем цену
        self.order_price = self.docs.size * price_per_kb
        self.save()

    def __str__(self) -> str:
        return f"Cart {self.id} - User {self.user.username} - Price {self.order_price} руб."
