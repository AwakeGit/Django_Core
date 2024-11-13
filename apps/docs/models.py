from django.conf import settings
from django.db import models


# Create your models here.
class Docs(models.Model):
    file_path = models.CharField(max_length=255)
    size = models.PositiveIntegerField()

    def __str__(self):
        return f"Doc {self.id}"


class UserToDocs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doc = models.ForeignKey(Docs, on_delete=models.CASCADE)

    def __str__(self):
        return f"User {self.user.id} - Docs {self.doc.id}"


class Price(models.Model):
    file_type = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.file_type} - {self.price}"
