# 로컬 개발환경 / 도커 가이드

이 문서는 도커를 처음 써보는 프로젝트라 힘든 부분이 많아서 작성한 가이드입니다.
"이럴 땐 뭘 쳐야 하지?"라는 상황별로 정리했으니, 외우려 하지 말고 필요할 때 검색하듯 찾아 쓰세요.

실제 설정 파일은 여기 두 개만 보면 됩니다:
- [Dockerfile](Dockerfile) — 앱 컨테이너가 어떻게 만들어지는지
- [docker-compose.yml](docker-compose.yml) — 앱 + DB가 어떻게 묶여서 뜨는지

---

## 큰 그림

우리 프로젝트는 컨테이너 두 개가 떠 있는 구조입니다.

```
[ app 컨테이너 ]  ←→  [ db 컨테이너 (postgres) ]
    :8000                  :5432
```

- **app**: Django + gunicorn이 돌아가는 컨테이너. 우리가 짠 코드가 들어갑니다.
- **db**: PostgreSQL 16. 데이터가 실제로 저장되는 곳.

두 컨테이너는 docker-compose가 만들어 주는 내부 네트워크로 연결돼 있어서,
app 컨테이너 안에서는 `db`라는 호스트명으로 DB에 접근할 수 있습니다.
(그래서 `docker-compose.yml`에서 `DB_HOST=db`로 덮어쓰고 있어요. 로컬에서는 'DB_HOST=localhost 로 동작)

---

## 볼륨 마운트

[docker-compose.yml](docker-compose.yml)의 app 서비스를 보면 이런 게 있습니다:

```yaml
volumes:
  - .:/app
  - /app/.venv
```

### `- .:/app`
내 컴퓨터의 현재 폴더(프로젝트 루트)를 컨테이너 안의 `/app`에 "연결"합니다.
**내 PC에서 코드를 수정하면 컨테이너 안의 코드도 같이 바뀝니다.** 이게 핵심.
덕분에 코드 고칠 때마다 이미지를 다시 빌드할 필요가 없어요.

### `- /app/.venv`
"`/app/.venv`는 마운트에서 제외한다"는 뜻입니다.
`.venv` 폴더가 저희 로컬에도 각자 있기 때문입니다.
이름이 같으니 덮어써버리는 일이 발생해 초반에 이 사유로 에러가 많이 났습니다.
그래서 "이 경로만 따로 관리해라"라고 분리해 두는 거예요.

---

## migrate는 자동으로 돼요

[Dockerfile](Dockerfile)의 마지막 줄을 보세요:

```
CMD ["sh", "-c", "uv run python manage.py migrate && ... && uv run gunicorn ..."]
```

컨테이너가 뜰 때마다 `migrate`가 먼저 돌고, 그 다음에 서버가 시작됩니다.
즉, **새 마이그레이션 파일을 pull 받은 뒤에는 컨테이너만 재시작하면 DB가 자동으로 반영됩니다.**
따로 `manage.py migrate`를 칠 필요가 없어요.

단, 모델을 "내가" 새로 고쳤다면 `makemigrations`는 해 줘야 합니다.
테이블(모델)에 수정사항이 생기면 그 내용을 반영하기 위한 새 마이그레이션 파일을 생성하는 작업이며 반드시 즉시 pr로 공유, 모두가 해당 파일을 pull 받아서 마이그레이트 할 수 있게 하셔야합니다.

---

## 상황별 4가지 명령어

"뭘 바꿨냐"에 따라 써야 할 명령어가 달라집니다.

### 1. `docker compose restart` — 그냥 재시작

코드만 고쳤는데 왠지 반영이 안 된 것 같을 때, 또는 서버를 다시 띄우고 싶을 때.

```bash
docker compose restart app
```

빠르고 가볍습니다. 이미지도 그대로, 볼륨도 그대로, 그냥 프로세스만 재시작.
사실 우리는 `- .:/app` 마운트 덕분에 코드 변경은 대부분 자동 반영되니 거의 쓸 일이 없습니다.


### 2. `docker compose up --build` — 이미지 다시 빌드

`pyproject.toml`에 변경사항이 있을 때, 즉 패키지(라이브러리)를 추가/삭제했을 때.
또는 `Dockerfile` 자체를 수정했을 때.

```bash
docker compose up --build
```

이미지를 처음부터 다시 만들기 때문에 `uv sync`가 다시 돕니다.
새 라이브러리가 설치되는 유일한 타이밍이에요.
**"패키지 새로 추가했는데 import 안 돼요!"** -> --build 빠뜨리신건지 확인


### 3. `docker compose down && docker compose up` — 컨테이너 완전 재생성

`docker-compose.yml`에서 환경 변수나 포트, 볼륨 설정을 바꿨을 때.

```bash
docker compose down
docker compose up
```

"설정 변경"은 기존 컨테이너에는 반영이 안 되기 때문에 이렇게 해야 합니다.
저희는 이 과정에 마이그레이트가 자동진행되기 때문에 마이그레이트를 위해서 up down 하는 경우가 많습니다.
데이터는 따로니 괜찮습니다.


### 4. `docker compose down -v` — 볼륨까지 다 밀어버리기

DB를 완전히 초기 상태로 되돌리고 싶을 때. (마이그레이션이 꼬여서 처음부터 다시 하고 싶을 때 등)

```bash
docker compose down -v
docker compose up --build
```

`-v` 플래그가 볼륨도 같이 지웁니다. **DB 데이터가 전부 날아갑니다.**
하지만 저희는 아직 찐 데이터가 없기때문에 괜찮습니다.


## 자주 쓰는 명령어

### 띄우기 / 내리기

```bash
# 포그라운드로 띄우기 (로그가 터미널에 쭉 나옴, Ctrl+C로 종료)
docker compose up

# 백그라운드로 띄우기 (터미널 다른 거 할 때 편함)
docker compose up -d

# 내리기
docker compose down
```

### 로그 보기

```bash
# 전체 로그 실시간으로 따라가기
docker compose logs -f

# app 컨테이너 로그만
docker compose logs -f app

# db 컨테이너 로그만
docker compose logs -f db
```

### 컨테이너 안에서 명령어 실행하기

`docker compose exec <서비스명> <명령어>` 형태

```bash
# 마이그레이션 파일 생성 (모델을 바꿨을 때)
docker compose exec app uv run python manage.py makemigrations

# 슈퍼유저 만들기
docker compose exec app uv run python manage.py createsuperuser

# Django shell 열기
docker compose exec app uv run python manage.py shell

# 그냥 컨테이너 안에 bash로 들어가기 (탐험하고 싶을 때)
docker compose exec app bash
```

### DB 직접 접속

```bash
# psql로 들어가기
docker compose exec db psql -U $DB_USER -d $DB_NAME
```

### 상태 확인

```bash
# 떠 있는 컨테이너 목록
docker compose ps
```

---

## 자주 하는 실수들

### "패키지 추가했는데 import가 안 돼요"
→ `pyproject.toml`에 추가만 하고 이미지를 다시 안 빌드한 경우입니다.
`docker compose up --build`로 다시 빌드하세요.

### "makemigrations 했는데 반영이 안 돼요"
→ `makemigrations`는 마이그레이션 **파일만** 만듭니다.
실제 DB 반영은 `migrate`인데, 이건 컨테이너가 뜰 때 자동으로 돌아요.
그러니 `makemigrations` 후에는 `docker compose restart app`으로 컨테이너를 재시작하면 됩니다.

### "내 PC에서 `manage.py` 치니까 에러가 나요"
→ 당연합니다. 우리는 컨테이너 안에서 돌리는 구조예요.
내 PC에는 파이썬 환경이 없어도 됩니다(있어도 되고요).
항상 `docker compose exec app uv run python manage.py ...` 형태로 치세요.
혹은 팀장에게 문의하세요.

### "DB가 이상해요, 그냥 싹 다 날리고 싶어요"
→ `docker compose down -v` 후에 다시 `docker compose up --build`.
**단, 이건 내 로컬 DB만 날아가는 거예요.** 팀 공용 DB가 아니니 겁먹지 말고 쓰세요.

### "포트 8000이 이미 사용 중이라는데요?"
→ 다른 프로세스가 8000 포트를 쓰고 있는 겁니다. 그 프로세스를 끄거나,
`docker-compose.yml`에서 포트를 `"8001:8000"` 식으로 바꿔 주세요.

---

## 핵심

1. **코드 수정은 자동 반영** — `- .:/app` 볼륨 마운트 덕분.
2. **migrate는 컨테이너 뜰 때 자동** — `makemigrations`만 수동으로.
3. **패키지 추가했으면 반드시 `--build`** — 안 그러면 설치 안 됨.
4. **DB 데이터는 `postgres_data` 볼륨에 있음** — `down`해도 안 지워지고, `down -v`해야 지워짐.
5. **컨테이너 안에서 명령어는 `docker compose exec app ...`** — 내 PC에서 직접 돌리려 하지 말 것.
