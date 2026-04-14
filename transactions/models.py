from django.db import models


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "입금"
        WITHDRAWAL = "withdrawal", "출금"

    class Category(models.TextChoices):
        FOOD = "food", "식비"
        TRANSPORT = "transport", "교통비"
        FIXED = "fixed", "고정비용"
        SAVINGS = "savings", "저축"
        LIVING = "living", "생활비"
        CULTURE = "culture", "문화생활"
        OTHER = "other", "기타"

    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    transacted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
