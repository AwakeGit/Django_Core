from django.conf import settings
from django.db import models


# Create your models here.
class Cart(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    docs_id = models.ForeignKey("docs.Docs", on_delete=models.CASCADE)
    order_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.BooleanField(default=False)
