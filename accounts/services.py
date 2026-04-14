from rest_framework.exceptions import PermissionDenied

from .models import Account


class AccountService:

    @staticmethod
    def get_accounts(user):
        return Account.objects.filter(user=user, is_active=True)

    @staticmethod
    def get_account(pk, user):
        try:
            return Account.objects.get(pk=pk, user=user, is_active=True)
        except Account.DoesNotExist:
            raise PermissionDenied("해당 계좌에 접근할 권한이 없습니다.")

    @staticmethod
    def create_account(serializer, user):
        return serializer.save(user=user)

    @staticmethod
    def delete_account(account):
        account.is_active = False
        account.save()
