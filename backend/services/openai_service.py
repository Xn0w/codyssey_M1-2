"""
openai_service.py
------------------
GPT API 호출을 담당.
1) "요약 정보를 시스템 프롬프트에 넣는다" - 컨텍스트 주입(Context Injection)
2) "GPT가 필요하면 우리 API를 도구로 직접 호출한다" - Function Calling (보너스 과제)

비유하자면, 컨텍스트 주입은 "비서에게 오늘자 브리핑 쪽지를 미리 쥐여주는 것"이고
Function Calling은 "비서가 브리핑에 없는 내용은 직접 서랍(DB)을 열어서 찾아보는 것"이다.
"""

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL
from services import firestore_service

# OPENAI_BASE_URL이 .env에 설정되어 있으면 그 주소로, 없으면 공식 OpenAI 서버로 요청을 보낸다.
if OPENAI_BASE_URL:
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
else:
    client = OpenAI(api_key=OPENAI_API_KEY)


def build_system_prompt(summary: dict) -> str:
    """계산된 요약 dict를 사람이 읽는 문장으로 바꿔서 시스템 프롬프트를 만든다."""
    if summary["count"] == 0:
        return (
            "당신은 사용자의 개인 데이터를 관리하는 AI 비서입니다. "
            "아직 저장된 데이터가 없습니다."
        )

    return (
        "당신은 사용자의 개인 시계열 데이터를 알고 있는 AI 비서입니다. "
        "아래 요약 정보를 참고해서 사용자 질문에 자연스럽고 구체적으로 답변하세요.\n\n"
        f"- 기간: {summary['period']['start']} ~ {summary['period']['end']}\n"
        f"- 데이터 개수: {summary['count']}개\n"
        f"- 평균값: {summary['average']}\n"
        f"- 최댓값: {summary['max']} / 최솟값: {summary['min']}\n"
        f"- 최근 추세: {summary['recent_trend']}\n\n"
        "요약에 없는 세부 수치를 함부로 지어내지 말고, 모르면 모른다고 답하세요. "
        "특정 날짜나 기간의 실제 개별 값이 필요하면(예: '7월 중순 값 알려줘'), "
        "지어내지 말고 반드시 get_data_in_range 도구를 호출해서 실제 데이터를 확인한 뒤 답변하세요."
    )


# ============ Function Calling 도구 정의 ============
# OpenAI Function Calling 스펙에 맞춘 "도구 명세서".
# GPT는 이 명세서를 보고 "이 도구를 부르면 뭘 받을 수 있는지" 판단한다.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_data_in_range",
            "description": (
                "사용자가 저장한 시계열 데이터 중, 지정한 기간(start_date~end_date)의 "
                "개별 데이터(날짜/값/메모)를 그대로 가져온다. "
                "요약 정보(평균/최댓값 등)만으로 답할 수 없는, 특정 날짜의 실제 값을 "
                "물어볼 때 사용한다."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "조회 시작 날짜, YYYY-MM-DD 형식",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "조회 종료 날짜, YYYY-MM-DD 형식",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    }
]


def _run_tool(name: str, arguments: dict) -> list[dict]:
    """GPT가 요청한 도구 이름/인자를 보고 실제 파이썬 함수를 실행한다."""
    if name == "get_data_in_range":
        return firestore_service.get_data_in_range(
            arguments["start_date"], arguments["end_date"]
        )
    raise ValueError(f"알 수 없는 도구 이름: {name}")


def get_chat_reply(system_prompt: str, history: list[dict], user_message: str) -> str:
    """
    history: [{"role": "user"/"assistant", "content": "..."}, ...] (기존 대화 맥락)

    흐름:
    1) 메시지 + 도구 명세(TOOLS)를 함께 GPT에 전달
    2) GPT가 "이건 도구 호출이 필요하다"고 판단하면 tool_calls를 응답에 담아 돌려준다
    3) 우리는 그 도구를 실제로 실행하고, 결과를 다시 GPT에게 넘긴다 (2차 호출)
    4) GPT가 도구 결과를 반영한 최종 답변을 만든다
    도구 호출이 필요 없는 평범한 질문이면 1번 호출로 바로 끝난다.
    """
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",  # 필요할 때만 GPT가 알아서 도구를 선택하도록 맡긴다
    )
    reply_message = response.choices[0].message

    # GPT가 도구 호출을 요청하지 않았다면, 바로 답변 반환하고 끝
    if not reply_message.tool_calls:
        return reply_message.content

    # ---- 여기서부터는 GPT가 도구 호출을 요청한 경우 ----
    import json

    messages.append(reply_message)  # GPT의 "도구를 부르겠다"는 응답도 대화 맥락에 포함시킨다

    for tool_call in reply_message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        tool_result = _run_tool(tool_call.function.name, args)

        # 도구 실행 결과를 "tool" role 메시지로 만들어 대화에 추가
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result, ensure_ascii=False),
        })

    # 도구 결과까지 포함해서 다시 한번 호출 -> 이번엔 최종 답변이 나온다
    final_response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
    )
    return final_response.choices[0].message.content