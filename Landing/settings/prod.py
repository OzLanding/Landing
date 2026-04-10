"""
운영(배포)용 설정. base.py 위에 보안/배포 관련 값을 덮어쓴다.
"""

import os

from .base import *  # noqa: F401,F403

DEBUG = False

# 환경변수에서 콤마로 구분된 호스트 목록을 읽음
# 예: ALLOWED_HOSTS="api.mysite.com,www.mysite.com"
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()
]

# 운영에서는 SECRET_KEY 가 환경변수로 반드시 주입되어야 함
if not os.environ.get("SECRET_KEY"):
    raise RuntimeError(
        "운영 환경에서는 SECRET_KEY 환경변수가 반드시 설정되어야 합니다."
    )

# CORS — 운영 환경에서는 허용할 프론트엔드 도메인을 환경변수로 관리
# 예: CORS_ALLOWED_ORIGINS="https://mysite.com,https://www.mysite.com"
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True

# 보안 헤더 (HTTPS 사용 시)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30일
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
