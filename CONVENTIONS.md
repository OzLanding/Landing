# 우리 팀 백엔드 컨벤션

실제로 이 패턴대로 짜여있는 코드를 보는 게 제일 빨라요:
- 단순한 예시는 [users/](users/) 앱
- 복잡한 예시는 [transactions/](transactions/) 앱

---

## 큰 그림

저희 프로젝트에서 클라이언트(브라우저)의 요청이 들어오면 아래의 순서로 데이터가 흘러갑니다.

```
URL → View → Serializer → Service → Repository → Model
```

각 단계는 "자기 일만" 합니다. 서로 남의 일을 침범하지 않는 게 핵심.
이 "책임 분리"가 가장 중요합니다.
문제가 생겼을 때, 이 문제가 어떤 단계의 책임인지 알면 바로 수정해야 할 곳을 알 수 있게 하는 것이 가장 큰 목표입니다.

각 단계에 대한 설명은 꼭 읽어주세요.

간단한 두 가지
models : 필드 정의, 관계 설정, 메타 클래스 작성
urls : 오직 라우팅만 합니다. url 내의 이름(보기 쉽게 login 처럼 기능 내용이 쓰여 있겠죠)을 보고, 해당 내용을 처리할 수 있는 적절한 views로 연결해 주는 역할. 끝.

---

## View — 최대한 얇게

View는 HTTP 창구 역할만 합니다.
urls에서 path를 따라 해당하는 views로 요청 내용을 보내면,
views는 그 요청을 받아서, 해당 요청에 필요한 기능을 가진 Service에 데이터를 넘기고, 받은 응답을 돌려줍니다.
이게 전부입니다.

실제로 작업을 진행하지 않습니다.
따라서 적절하게 service 기능에게 데이터를 넘겨주고, 잘 받아오고, 그걸 또 잘 리턴해 주는 역할입니다.

**즉 -> View 안에 절대 들어가면 안 되는 것:**
- 비즈니스 로직 (if문으로 도메인 규칙 따지는 거) : Service
- 계산, 상태 변경 : Service
- DB 쿼리 (직접 `Model.objects.filter(...)` 호출) : Repository

ps. 도메인 규칙이란
본인 소유 계좌인지 확인 거침, 출금 시 잔액 부족하면 거부 -> 이런 내용들이 도메인 규칙 따지는 일
즉 service 단계에 있어야 할 내용입니다.


### View 베이스

**기본 규칙: `APIView`를 씁니다.**

`users`, `accounts` 앱은 `APIView`를 상속해서 `get`, `post`, `put`, `delete` 메서드를 직접 작성합니다.
Generic View의 훅(hook) 메서드 (`get_queryset`, `perform_create`) 등을 쓰지 않습니다.

(트랜잭션 앱만 예외입니다.)

```python
class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserService.signup(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

코드를 보면 요청이 들어와서 → 검증 → Service 호출 → 응답 반환하는 흐름이 한눈에 보입니다.
"숨은 동작이 없음"이 Generic View와 다른 현재 가장 중요한 점이라고 보시면 됩니다.
(배우고 있는 입장)


## Serializer — 검증 전문가

Serializer는 들어오는 데이터가 올바른지 확인하고, 나가는 데이터를 JSON으로 말아 주는 역할만 합니다.
FastAPI 기준으로 스키마를 떠올려 보시면 좀 더 이해가 잘 되실 것 같습니다.

단일 필드 검증은 `validate_<필드명>`, 여러 필드를 같이 봐야 하는 검증은 `validate` 쓰면 됩니다.
장고에 있으니 임포트해서 쓰시면 됩니다.

응답에 연관 객체 정보를 넣고 싶을 때는 별도의 `*SummarySerializer`를 정의해서 중첩시킵니다.
응답 전용 필드와 요청 전용 필드가 깔끔하게 분리되어야 합니다. 아래는 트랜잭션 앱에 이미 구현되어 있는 예시입니다.

[transactions/serializers.py](transactions/serializers.py):

```python
class TransactionSerializer(serializers.ModelSerializer):
    account_detail = AccountSummarySerializer(source="account", read_only=True)

    class Meta:
        model = Transaction
        fields = [...]
        read_only_fields = ["id", "balance_after", "created_at"]
        extra_kwargs = {"account": {"write_only": True}}

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("거래 금액은 0보다 커야 합니다.")
        return value
```

---

## Service — 진짜 일은 여기서!!!

가장 중요한 레이어입니다.
비즈니스 로직, 도메인 규칙, 권한 확인, 상태 변경을 실제로 수행합니다.
어떤 도메인이 실제로 어떻게 동작하는지 해당 앱의 `services.py`만 보면 알 수 있어야 합니다.

### 컨벤션 반드시 숙지해 주세요:

- 파일은 `<앱이름>/services.py`, 클래스는 `<도메인>Service`
  (예: `UserService`, `TransactionService`)
- 메서드는 전부 `@staticmethod` (Service는 상태를 가지지 않습니다.)
- **여러 모델에 쓰기가 일어나거나, 중간에 실패하면 롤백되어야 할 때**는 `db_transaction.atomic()`으로 감쌉니다.
  "이 중에서 한 개만 실패해도 작업 자체를 진행하지 않게 한다"라고 생각해 주세요.
- 단일 쿼리 작업에는 `atomic()`을 쓰지 마세요. 어차피 감싸는 의미가 없습니다.
- Django의 `transaction` 모듈은 우리 `transactions` 앱과 이름이 겹치니까 항상 `as db_transaction`으로 별칭해서 씁니다.
- 도메인 규칙을 어겼을 때는 DRF 예외를 던집니다:
  - 권한 문제면 `PermissionDenied`
  - 데이터나 상태 문제면 `ValidationError`
- Service에서 던진 예외는 View나 Serializer에서 잡지 마세요. DRF가 알아서 HTTP 응답으로 변환해 줍니다.


atomic 예시 — [transactions/services.py](transactions/services.py)

거래를 생성할 때 계좌 소유권 확인 → 활성 상태 확인 → 잔액 계산 → 계좌와 거래를 동시에 저장하는 흐름입니다.
계좌 업데이트와 거래 저장은 반드시 함께 성공하거나 실패해야 하니까 `atomic()`이 꼭 필요해요.
분리되면 절대 안 됩니다. 나라 경제가 무너지고 세계가 망가지고...

```python
from django.db import transaction as db_transaction
from rest_framework.exceptions import PermissionDenied, ValidationError


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

            account.save(update_fields=["balance"])
            return serializer.save(balance_after=account.balance)
```

단일 쿼리 작업 — [users/services.py](users/services.py)

회원가입은 유저 하나 만드는 게 전부라서 INSERT 단일 쿼리라 `atomic()`도 필요 없습니다.

```python
class UserService:

    @staticmethod
    def signup(serializer) -> User:
        validated_data = dict(serializer.validated_data)
        validated_data.pop("password2")
        password = validated_data.pop("password")

        return User.objects.create_user(password=password, **validated_data)
```

여기서 Service가 하는 일은 여기까지입니다.
`User.objects.create_user(...)`를 호출해 유저를 "실제로 생성"하고, 생성된 객체를 View로 반환하는 것까지.

View가 Service가 반환한 값을 받아서 `Response(serializer.data, status=201)` 같은 형태로 포장해 클라이언트에 돌려줍니다.

- **Service**: 실제 생성/상태 변경 + 결과 반환
- **View**: Service 호출 + 받은 응답 포장 + 반환

이 책임 분리가 문서 전체에서 계속 반복하고 있는 중요한 부분입니다.

---

## Repository — 선택사항

"복잡한" 쿼리(필터링, 정렬, `select_related` 최적화)는 Repository에 모아 둡니다.
Service나 View가 쿼리 세부 사항에 신경 쓰지 않아도 되게 하는 역할입니다.

- 파일은 `<앱이름>/repositories.py`, 클래스는 `<도메인>Repository`
- 메서드는 `@staticmethod`
- **단순한 CRUD만 필요한 앱에서는 Repository를 만들지 않아도 됩니다.** `Model.objects.get(pk=...)` 수준이면 그냥 Service에서 직접 쿼리하세요.

실제 예시 — [transactions/repositories.py](transactions/repositories.py):

```python
class TransactionRepository:

    @staticmethod
    def get_user_transactions(user) -> QuerySet[Transaction]:
        return (
            Transaction.objects.filter(account__user=user)
            .select_related("account")
            .order_by("-transacted_at")
        )

    @staticmethod
    def apply_filters(queryset, filters: dict) -> QuerySet[Transaction]:
        if transaction_type := filters.get("transaction_type"):
            queryset = queryset.filter(transaction_type=transaction_type)
        # ...
        return queryset
```

transactions 앱은 필터가 많아서 Repository를 분리하는 게 낫지만, users 앱은 쿼리가 단순해서 Repository 자체가 없습니다. 필요할 때만 만드세요.

---

## 핵심

1. **View는 얇다.** 비즈니스 로직 없음. Service 부르고 응답만.
2. **Service가 모든 걸 한다.** 도메인 규칙, 권한, 상태 변경.
3. **Repository는 복잡한 쿼리가 있을 때만** 만든다.
4. **DB에 동시에 두 개 이상 써야 할 때는 `db_transaction.atomic()` 사용, 단일 작성은 감싸지 말 것.**
   DB 작성(INSERT/UPDATE/DELETE) 여러 개가 하나의 동작으로 묶여야 할 때를 말함!
5. **예외는 `ValidationError` / `PermissionDenied`**로 Service에서 던진다.
6. **`django.db.transaction`은 항상 `as db_transaction`으로 별칭을 부여해 혼란 방지**.

---

## 예외

ex)
읽기 전용의 엄청 단순한 엔드포인트라면 Service를 생략하고 View에서 Repository를 직접 불러도 괜찮습니다.
단, 팀원들이 인지할 수 있게 반드시 PR에서 언급하고 이유를 남겨 주세요!
