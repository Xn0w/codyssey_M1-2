"""
main.py
-------
FastAPI 앱의 진입점. 로컬 실행: uvicorn main:app --reload
Swagger UI 확인: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from routers import data, conversations, chat

app = FastAPI(title="나만의 AI 비서 API")

# 프론트엔드(다른 도메인)에서 이 API를 호출할 수 있도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
def health_check():
    """배포 후 서버가 살아있는지 빠르게 확인하는 용도."""
    return {"status": "ok", "message": "AI 비서 서버가 정상 동작 중입니다."}
