from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(
        max_length=50,
        validators=[
            UniqueValidator(
                queryset=Account.objects.all(),
                message="이미 등록된 계좌번호입니다.",
            )
        ]
    )

    class Meta:
        model = Account
        fields = [
            'id',
            'account_number',
            'bank_name',
            'balance',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'balance', 'created_at']
