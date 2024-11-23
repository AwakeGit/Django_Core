# config/management/commands/wait_for_db.py

import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Ожидает доступности базы данных перед запуском приложения"

    def handle(self, *args, **options):
        self.stdout.write("Ожидание доступности базы данных...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections["default"]
                # c = db_conn.cursor()
            except OperationalError:
                self.stdout.write(
                    "База данных недоступна, повторная проверка через 1 секунду..."
                )
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("База данных доступна!"))
