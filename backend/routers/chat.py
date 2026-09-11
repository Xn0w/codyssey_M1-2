"""
routers/chat.py
----------------
'/api/chat' — 이 프로젝트의 심장.
흐름: 요약 조회 -> 시스템 프롬프트 조립 -> (기존 맥락 + 새 질문)으로 GPT 호출
      -> 사용자/AI 메시지 둘 다 저장 -> 응답 반환
"""

from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse
from services import firestore_service, summary_service, openai_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest):
    # 1) 대화가 없으면 새로 생성 (첫 메시지 앞부분을 제목으로 사용)
    if payload.conversation_id:
        conversation = firestore_service.get_conversation(payload.conversation_id)
    else:
        title = payload.message[:20]  # 제목이 너무 길지 않게 앞부분만 사용
        conversation = firestore_service.create_conversation(title)

    conversation_id = conversation["id"]
    history = conversation.get("messages", [])

    # 2) 데이터 요약 조회 후 시스템 프롬프트 조립 (컨텍스트 주입)
    items = firestore_service.list_data_items()
    summary = summary_service.calculate_summary(items)
    system_prompt = openai_service.build_system_prompt(summary)

    # 3) GPT 호출
    reply = openai_service.get_chat_reply(system_prompt, history, payload.message)

    # 4) 사용자 메시지 + AI 응답을 대화 기록에 자동 저장
    firestore_service.append_message(conversation_id, "user", payload.message)
    firestore_service.append_message(conversation_id, "assistant", reply)

    return ChatResponse(conversation_id=conversation_id, reply=reply)
