from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class Docs(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="Пользователь"
    )
    file = models.FileField(
        upload_to="uploads/",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "pdf"]),
        ],
        help_text="Файл",
    )
    size = models.PositiveIntegerField(help_text="Размер файла в КБ")
    payment_status = models.BooleanField(default=False, help_text="Статус оплаты")
    analysis_done = models.BooleanField(
        default=False, help_text="Статус выполнения анализа"
    )
    text = models.TextField(null=True, blank=True, help_text="Текст из файла")
    fastapi_id = models.PositiveIntegerField(help_text="id")

    def __str__(self):
        return f"Doc {self.id} ({self.user.username})"


class UserToDocs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doc = models.ForeignKey(Docs, on_delete=models.CASCADE)

    def __str__(self):
        return f"User {self.user.id} - Docs {self.doc.id}"


class Price(models.Model):
    file_type = models.CharField(max_length=255, help_text="Тип файла (расширение)")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Цена за анализ 1 КБ"
    )

    def __str__(self):
        return f"{self.file_type} - {self.price} руб./КБ"
