from django.core.management.base import BaseCommand

from apps.docs.models import Price


class Command(BaseCommand):
    help = "Инициализирует модель Price с базовыми ценами."

    def handle(self, *args, **options):
        prices = [
            {"file_type": "jpg", "price": 0.05},
            {"file_type": "jpeg", "price": 0.05},
            {"file_type": "png", "price": 0.07},
            {"file_type": "pdf", "price": 0.10},
        ]
        for price_data in prices:
            Price.objects.update_or_create(
                file_type=price_data["file_type"],
                defaults={"price": price_data["price"]},
            )
        self.stdout.write(self.style.SUCCESS("Модель Price успешно инициализирована."))
