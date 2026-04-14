from django.contrib import admin

from transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "account",
        "transaction_type",
        "category",
        "amount",
        "balance_after",
        "transacted_at",
    ]
    list_filter = ["transaction_type", "category"]
    search_fields = ["description"]
    ordering = ["-transacted_at"]
    readonly_fields = ["created_at"]
