from rest_framework import serializers

from transactions.models import Transaction


class AccountSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    account_number = serializers.CharField(read_only=True)
    bank_name = serializers.CharField(read_only=True)


class TransactionSerializer(serializers.ModelSerializer):
    account_detail = AccountSummarySerializer(source="account", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "account_detail",
            "transaction_type",
            "category",
            "amount",
            "balance_after",
            "description",
            "transacted_at",
            "created_at",
        ]
        read_only_fields = ["id", "balance_after", "created_at"]
        extra_kwargs = {
            "account": {"write_only": True},
        }

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("거래 금액은 0보다 커야 합니다.")
        return value


class TransactionDetailSerializer(serializers.ModelSerializer):
    account_detail = AccountSummarySerializer(source="account", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "account_detail",
            "transaction_type",
            "category",
            "amount",
            "balance_after",
            "description",
            "transacted_at",
            "created_at",
        ]
        read_only_fields = ["id", "account", "balance_after", "created_at"]
