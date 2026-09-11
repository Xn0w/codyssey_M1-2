"""
config.py
---------
환경변수(.env)를 읽어와서 다른 파일들이 공통으로 가져다 쓸 수 있게 정리하는 곳.
비유하자면 "사무실 열쇠 보관함" 같은 역할 — 여기서만 열쇠(키)를 꺼내 쓰고,
다른 코드에는 절대 키 값을 하드코딩하지 않는다.
"""

import os
from dotenv import load_dotenv

# .env 파일에 적어둔 값들을 환경변수로 불러온다.
load_dotenv()

# OpenAI API 키
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Firebase 서비스 계정 키 JSON 파일 경로
# (Firebase 콘솔 > 프로젝트 설정 > 서비스 계정 > 새 비공개 키 생성으로 받은 파일)
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-key.json")

# 프론트엔드 배포 주소 (CORS 허용용). 여러 개면 쉼표로 구분해서 .env에 적는다.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500").split(",")

# 필수 값이 비어있으면 서버 켜자마자 바로 알아차리도록 방어 코드
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY가 .env에 설정되어 있지 않습니다.")
