"""
schemas.py
----------
Pydantic 모델 모음. FastAPI는 이 모델을 보고 자동으로
"요청 데이터가 형식에 맞는지" 검증하고, 틀리면 알아서 422 에러를 돌려준다.
JSP 시절로 치면 VO(Value Object) + 유효성 검증(validation)을 한 번에 하는 셈.
"""

from pydantic import BaseModel
from typing import Optional, List


# ---------- 시계열 데이터 (data 컬렉션) ----------

class DataItem(BaseModel):
    """데이터 추가(POST) 시 사용하는 모델. 세 필드 모두 필수."""
    date: str          # 예: "2026-09-01"
    value: float        # 예: 72500.0 (주가, 온도 등 뭐든 가능)
    memo: Optional[str] = ""   # 메모는 선택 입력


class DataItemUpdate(BaseModel):
    """데이터 수정(PUT) 시 사용하는 모델. 부분 수정을 허용하려고 전부 Optional."""
    date: Optional[str] = None
    value: Optional[float] = None
    memo: Optional[str] = None


class DataItemResponse(DataItem):
    """조회 시 응답에 쓰는 모델. Firestore 문서 id를 추가로 포함한다."""
    id: str


# ---------- 대화 기록 (conversations 컬렉션) ----------

class Message(BaseModel):
    role: str        # "user" 또는 "assistant"
    content: str


class ConversationCreate(BaseModel):
    """새 대화를 시작할 때 (제목은 없어도 되고, 첫 메시지로 자동 생성해도 됨)."""
    title: Optional[str] = "새 대화"


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: Optional[str] = None
    messages: Optional[List[Message]] = None  # 목록 조회 시엔 생략, 단건 조회 시엔 포함


# ---------- 채팅 (chat) ----------

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None  # 없으면 새 대화를 만들어서 진행


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
