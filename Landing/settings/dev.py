"""
로컬 개발용 설정. base.py 의 모든 값을 그대로 쓰고, 개발 편의를 위한 값만 덮어쓴다.
"""

from .base import *  # noqa: F401,F403

DEBUG = True

# 개발 중엔 모든 호스트 허용 (runserver, docker, 다른 기기에서 접속 등)
ALLOWED_HOSTS = ["*"]
