"""
openai_service.py
------------------
GPT API 호출을 담당. "요약 정보를 시스템 프롬프트에 넣는다"는
컨텍스트 주입(Context Injection)의 핵심 로직이 여기 있다.
"""

from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def build_system_prompt(summary: dict) -> str:
    """계산된 요약 dict를 사람이 읽는 문장으로 바꿔서 시스템 프롬프트를 만든다."""
    if summary["count"] == 0:
        return "당신은 사용자의 개인 데이터를 관리하는 AI 비서입니다. 아직 저장된 데이터가 없습니다."

    return (
        "당신은 사용자의 개인 시계열 데이터를 알고 있는 AI 비서입니다. "
        "아래 요약 정보를 참고해서 사용자 질문에 자연스럽고 구체적으로 답변하세요.\n\n"
        f"- 기간: {summary['period']['start']} ~ {summary['period']['end']}\n"
        f"- 데이터 개수: {summary['count']}개\n"
        f"- 평균값: {summary['average']}\n"
        f"- 최댓값: {summary['max']} / 최솟값: {summary['min']}\n"
        f"- 최근 추세: {summary['recent_trend']}\n\n"
        "요약에 없는 세부 수치를 함부로 지어내지 말고, 모르면 모른다고 답하세요."
    )


def get_chat_reply(system_prompt: str, history: list[dict], user_message: str) -> str:
    """
    history: [{"role": "user"/"assistant", "content": "..."}, ...] (기존 대화 맥락)
    OpenAI Chat Completions 형식에 맞춰 메시지 리스트를 조립해서 호출한다.
    """
    messages = [{"role": "system", "content": system_prompt}]

    # 과거 대화 맥락을 이어붙인다 (role/content만 남기고 timestamp는 제외)
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
    )
    return response.choices[0].message.content
