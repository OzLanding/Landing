# 📋 transactions 브랜치 수정 요청

머지 전 아래 항목들 **그대로** 반영해주세요. 코드 스니펫 그대로 복붙하시면 됩니다.

---

## 1. `transactions/models.py` — 전체 교체

아래 내용으로 **파일 전체를 교체**해주세요.

```python
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
        null=False,
        blank=False,
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        null=False,
        blank=False,
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        null=False,
        blank=False,
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=False,
        blank=False,
    )
    balance_after = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=False,
        blank=False,
    )
    description = models.CharField(max_length=255, blank=True)
    transacted_at = models.DateTimeField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
```

**변경 포인트:**
- `extra_fields` 필드 **삭제**
- `account` FK의 `null=True, blank=True` → `null=False, blank=False`로 변경
- NOT NULL인 컬럼들 전부 `null=False, blank=False` 명시
- `description`은 선택 입력 필드라 `blank=True` 유지 (문자열 필드는 `null=True` 대신 빈 문자열 사용이 Django 컨벤션)

---

## 2. `transactions/serializers.py` — `extra_fields` 제거

`fields` 리스트에서 `'extra_fields'` 한 줄만 제거해주세요.

```python
from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'account',
            'transaction_type',
            'category',
            'amount',
            'balance_after',
            'description',
            'transacted_at',
            'created_at',
        ]
        read_only_fields = ['created_at']
```

---

## 3. `.gitignore` — `__pycache__/` 복구

`.venv/` 아래줄에 `__pycache__/` 다시 추가해주세요.

```gitignore
# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
```

---

## 4. `django-filter` 패키지 설치

`filters.py`에서 `django_filters` 쓰는데 패키지가 없어요. 아래 명령어로 설치해주세요.

```bash
uv add django-filter
```

그리고 **`Landing/settings/base.py`의 `THIRD_PARTY_APPS`에 추가**해주세요.

```python
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
]
```

> ⚠️ 주의: 패키지 이름은 `django-filter`(하이픈)이지만, INSTALLED_APPS에 넣을 땐 `django_filters`(언더스코어 + 복수형 s)입니다. 헷갈리기 쉬우니 꼭 확인해주세요.

---

## 5. `transactions/tests.py` — User 생성 방식 수정

저희 커스텀 User 모델은 `USERNAME_FIELD = "email"`이라 positional 인자 꼬일 수 있어요. **모든 `create_user` 호출을 키워드 인자로 명시**해주세요.

**변경 전 (❌):**
```python
self.user = User.objects.create_user(
    username='testuser',
    email='test@test.com',
    password='password'
)
```

**변경 후 (✅):**
```python
self.user = User.objects.create_user(
    email='test@test.com',
    password='password',
    username='testuser',
)
```

`other_user` 생성 부분도 똑같이 바꿔주세요.

---

## 6. 마이그레이션 파일은 생성하지 마세요 ❌

`makemigrations` **돌리지 마세요.** 팀장 브랜치랑 겹쳐서 문제 생겨요. 머지 이후 따로 처리할게요.

---

## ✅ 체크리스트 (push 전 확인)

- [ ] `models.py`에서 `extra_fields` 삭제됨
- [ ] `models.py`의 `account` FK가 `null=False, blank=False`로 되어 있음
- [ ] `models.py`의 NOT NULL 필드들에 `null=False, blank=False` 명시됨
- [ ] `serializers.py`에서 `extra_fields` 제거됨
- [ ] `.gitignore`에 `__pycache__/` 복구됨
- [ ] `uv add django-filter` 실행함 (`pyproject.toml`, `uv.lock` 변경됨)
- [ ] `Landing/settings/base.py`의 `THIRD_PARTY_APPS`에 `"django_filters"` 추가됨
- [ ] `tests.py`의 `create_user` 호출이 전부 키워드 인자로 되어 있음
- [ ] `transactions/migrations/` 폴더에 **새 파일 없음** (makemigrations 돌리지 않음)
