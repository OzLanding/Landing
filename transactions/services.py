from django.db import transaction as db_transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from transactions.models import Transaction


class TransactionService:

    @staticmethod
    def create_transaction(user, serializer) -> Transaction:
        account = serializer.validated_data["account"]

        if account.user_id != user.id:
            raise PermissionDenied("본인 소유의 계좌에만 거래를 생성할 수 있습니다.")

        if not account.is_active:
            raise ValidationError("비활성화된 계좌에는 거래를 생성할 수 없습니다.")

        amount = serializer.validated_data["amount"]
        transaction_type = serializer.validated_data["transaction_type"]

        with db_transaction.atomic():
            if transaction_type == Transaction.TransactionType.DEPOSIT:
                account.balance += amount
            else:
                if account.balance < amount:
                    raise ValidationError("잔액이 부족합니다.")
                account.balance -= amount

            balance_after = account.balance
            account.save(update_fields=["balance"])

            return serializer.save(balance_after=balance_after)

    @staticmethod
    def update_transaction(instance: Transaction, serializer) -> Transaction:
        old_amount = instance.amount
        old_type = instance.transaction_type
        new_amount = serializer.validated_data.get("amount", old_amount)
        new_type = serializer.validated_data.get("transaction_type", old_type)

        account = instance.account

        with db_transaction.atomic():
            if old_type == Transaction.TransactionType.DEPOSIT:
                account.balance -= old_amount
            else:
                account.balance += old_amount

            if new_type == Transaction.TransactionType.DEPOSIT:
                account.balance += new_amount
            else:
                if account.balance < new_amount:
                    raise ValidationError("잔액이 부족합니다.")
                account.balance -= new_amount

            balance_after = account.balance
            account.save(update_fields=["balance"])

            return serializer.save(balance_after=balance_after)

    @staticmethod
    def delete_transaction(instance: Transaction) -> None:
        account = instance.account

        with db_transaction.atomic():
            if instance.transaction_type == Transaction.TransactionType.DEPOSIT:
                if account.balance < instance.amount:
                    raise ValidationError(
                        "해당 입금 거래를 삭제하면 잔액이 음수가 됩니다."
                    )
                account.balance -= instance.amount
            else:
                account.balance += instance.amount

            account.save(update_fields=["balance"])
            instance.delete()
