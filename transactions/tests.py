from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Account
from transactions.models import Transaction
from users.models import User

LIST_CREATE_URL = reverse("transaction-list-create")


def detail_url(pk):
    return reverse("transaction-detail", kwargs={"pk": pk})


class TransactionTestBase(APITestCase):
    """공통 fixture를 제공하는 베이스 클래스."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            username="tester",
        )
        cls.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123",
            username="other",
        )
        cls.account = Account.objects.create(
            user=cls.user,
            account_number="1234567890",
            bank_name="카카오뱅크",
            balance=Decimal("100000.00"),
        )
        cls.other_account = Account.objects.create(
            user=cls.other_user,
            account_number="9876543210",
            bank_name="신한은행",
            balance=Decimal("50000.00"),
        )

    def create_transaction(self, account=None, **overrides):
        defaults = {
            "account": account or self.account,
            "transaction_type": Transaction.TransactionType.DEPOSIT,
            "category": Transaction.Category.OTHER,
            "amount": Decimal("10000.00"),
            "balance_after": Decimal("110000.00"),
            "description": "테스트 거래",
            "transacted_at": timezone.now(),
        }
        defaults.update(overrides)
        return Transaction.objects.create(**defaults)


class TransactionCreateTests(TransactionTestBase):

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_deposit(self):
        data = {
            "account": self.account.id,
            "transaction_type": "deposit",
            "category": "food",
            "amount": "5000.00",
            "description": "용돈 입금",
            "transacted_at": timezone.now().isoformat(),
        }
        response = self.client.post(LIST_CREATE_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["balance_after"], "105000.00")
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("105000.00"))

    def test_create_withdrawal(self):
        data = {
            "account": self.account.id,
            "transaction_type": "withdrawal",
            "category": "food",
            "amount": "3000.00",
            "description": "점심 식대",
            "transacted_at": timezone.now().isoformat(),
        }
        response = self.client.post(LIST_CREATE_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["balance_after"], "97000.00")
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("97000.00"))

    def test_withdrawal_insufficient_balance(self):
        data = {
            "account": self.account.id,
            "transaction_type": "withdrawal",
            "category": "other",
            "amount": "999999.00",
            "description": "잔액 초과 출금 시도",
            "transacted_at": timezone.now().isoformat(),
        }
        response = self.client.post(LIST_CREATE_URL, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_zero_amount_rejected(self):
        data = {
            "account": self.account.id,
            "transaction_type": "deposit",
            "category": "other",
            "amount": "0",
            "transacted_at": timezone.now().isoformat(),
        }
        response = self.client.post(LIST_CREATE_URL, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_on_other_users_account(self):
        data = {
            "account": self.other_account.id,
            "transaction_type": "deposit",
            "category": "other",
            "amount": "1000.00",
            "transacted_at": timezone.now().isoformat(),
        }
        response = self.client.post(LIST_CREATE_URL, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TransactionListTests(TransactionTestBase):

    def setUp(self):
        self.client.force_authenticate(user=self.user)
        self.tx1 = self.create_transaction(
            transaction_type=Transaction.TransactionType.DEPOSIT,
            category=Transaction.Category.FOOD,
            amount=Decimal("5000.00"),
        )
        self.tx2 = self.create_transaction(
            transaction_type=Transaction.TransactionType.WITHDRAWAL,
            category=Transaction.Category.TRANSPORT,
            amount=Decimal("2000.00"),
        )
        self.create_transaction(account=self.other_account)

    def test_list_returns_only_own_transactions(self):
        response = self.client.get(LIST_CREATE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_contains_required_fields(self):
        response = self.client.get(LIST_CREATE_URL)
        item = response.data[0]

        self.assertIn("account_detail", item)
        self.assertIn("transaction_type", item)
        self.assertIn("amount", item)
        self.assertIn("transacted_at", item)

    def test_filter_by_transaction_type(self):
        response = self.client.get(LIST_CREATE_URL, {"transaction_type": "deposit"})

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["transaction_type"], "deposit")

    def test_filter_by_category(self):
        response = self.client.get(LIST_CREATE_URL, {"category": "food"})

        self.assertEqual(len(response.data), 1)

    def test_filter_by_amount_range(self):
        response = self.client.get(
            LIST_CREATE_URL, {"min_amount": "3000", "max_amount": "6000"}
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["amount"], "5000.00")


class TransactionDetailTests(TransactionTestBase):

    def setUp(self):
        self.client.force_authenticate(user=self.user)
        self.tx = self.create_transaction()

    def test_retrieve_own_transaction(self):
        response = self.client.get(detail_url(self.tx.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.tx.pk)

    def test_cannot_retrieve_other_users_transaction(self):
        other_tx = self.create_transaction(account=self.other_account)
        response = self.client.get(detail_url(other_tx.pk))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_transaction(self):
        data = {"description": "수정된 설명", "amount": "20000.00"}
        response = self.client.patch(detail_url(self.tx.pk), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tx.refresh_from_db()
        self.assertEqual(self.tx.description, "수정된 설명")

    def test_delete_transaction_restores_balance(self):
        deposit_tx = self.create_transaction(
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=Decimal("5000.00"),
            balance_after=Decimal("105000.00"),
        )
        self.account.balance = Decimal("105000.00")
        self.account.save()

        response = self.client.delete(detail_url(deposit_tx.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("100000.00"))


class TransactionAuthTests(TransactionTestBase):

    def test_unauthenticated_list_blocked(self):
        response = self.client.get(LIST_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_create_blocked(self):
        data = {
            "account": self.account.id,
            "transaction_type": "deposit",
            "category": "other",
            "amount": "1000.00",
            "transacted_at": timezone.now().isoformat(),
        }
        response = self.client.post(LIST_CREATE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_detail_blocked(self):
        tx = self.create_transaction()
        response = self.client.get(detail_url(tx.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
