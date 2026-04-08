from django.db.models import QuerySet

from transactions.models import Transaction


class TransactionRepository:

    @staticmethod
    def get_user_transactions(user) -> QuerySet[Transaction]:
        return (
            Transaction.objects.filter(account__user=user)
            .select_related("account")
            .order_by("-transacted_at")
        )

    @staticmethod
    def apply_filters(queryset: QuerySet[Transaction], filters: dict) -> QuerySet[Transaction]:
        if transaction_type := filters.get("transaction_type"):
            queryset = queryset.filter(transaction_type=transaction_type)

        if category := filters.get("category"):
            queryset = queryset.filter(category=category)

        if min_amount := filters.get("min_amount"):
            queryset = queryset.filter(amount__gte=min_amount)

        if max_amount := filters.get("max_amount"):
            queryset = queryset.filter(amount__lte=max_amount)

        if start_date := filters.get("start_date"):
            queryset = queryset.filter(transacted_at__gte=start_date)

        if end_date := filters.get("end_date"):
            queryset = queryset.filter(transacted_at__lte=end_date)

        return queryset
