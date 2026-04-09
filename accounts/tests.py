from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from .models import Account

User = get_user_model()


class AccountAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password'
        )
        self.client.force_authenticate(user=self.user)

    # 계좌 생성
    def test_create_account(self):
        data = {
            'account_number': '1234567890',
            'bank_name': '국민은행',
        }
        res = self.client.post('/api/accounts/', data)
        self.assertEqual(res.status_code, 201)

    # 계좌 목록 조회
    def test_list_accounts(self):
        Account.objects.create(
            user=self.user,
            account_number='1234567890',
            bank_name='국민은행'
        )
        res = self.client.get('/api/accounts/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    # 다른 유저 계좌 접근 차단
    def test_cannot_access_other_user_account(self):
        other_user = User.objects.create_user(
            username='other', email='other@test.com', password='pass'
        )
        other_account = Account.objects.create(
            user=other_user,
            account_number='9999999999',
            bank_name='신한은행'
        )
        res = self.client.get(f'/api/accounts/{other_account.id}/')
        self.assertEqual(res.status_code, 403)

    # 소프트 삭제
    def test_delete_account(self):
        account = Account.objects.create(
            user=self.user,
            account_number='1234567890',
            bank_name='국민은행'
        )
        res = self.client.delete(f'/api/accounts/{account.id}/')
        self.assertEqual(res.status_code, 204)
        account.refresh_from_db()
        self.assertFalse(account.is_active)