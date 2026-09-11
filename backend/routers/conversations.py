"""
routers/conversations.py
-------------------------
'/api/conversations' 관련 엔드포인트.
목록 조회는 가볍게(messages 제외), 단건 조회는 messages 전체 포함 — 이걸
README에 "설계 결정"으로 명시하면 과제 요구사항(옵션 A)을 충족한다.
"""

from fastapi import APIRouter, HTTPException

from models.schemas import ConversationCreate, ConversationResponse
from services import firestore_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse)
def create_conversation(payload: ConversationCreate):
    return firestore_service.create_conversation(payload.title)


@router.get("", response_model=list[ConversationResponse])
def list_conversations():
    # 목록 조회 응답에는 messages를 포함하지 않는다 (가벼운 목록용)
    return firestore_service.list_conversations()


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str):
    conv = firestore_service.get_conversation(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return conv


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    firestore_service.delete_conversation(conversation_id)
    return {"message": "삭제되었습니다.", "id": conversation_id}
