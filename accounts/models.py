from django.conf import settings
from django.db import models


class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
    )
    account_number = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"