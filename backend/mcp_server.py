"""
mcp_server.py
-------------
보너스 과제: 동일 기능을 MCP Server로도 연동해서 외부 채널(클라이언트)에서
검증하기 위한 파일.

지금까지 만든 "GPT가 부르는 도구"(services/openai_service.py의 TOOLS)와
개념은 완전히 같다. 다만 이번엔 GPT가 아니라, Claude Desktop 같은
'MCP를 지원하는 외부 AI 클라이언트'가 이 도구를 부를 수 있게 만드는 것이다.

비유하면: openai_service.py의 도구 호출은 "우리 집 비서(GPT)만 쓰는 전용 문"이고,
이 MCP 서버는 "다른 집 손님(Claude 등 외부 클라이언트)도 초인종 눌러서
같은 서랍(Firestore 데이터)을 조회할 수 있게 만든 정문"이다.

실행 방법 (backend 폴더 안에서):
    mcp dev mcp_server.py
그러면 브라우저에 MCP Inspector가 열리고, 거기서 도구를 직접 호출해볼 수 있다.
"""

from mcp.server.mcpserver import MCPServer

from services import firestore_service, summary_service

# 서버 이름 - MCP 클라이언트 쪽에 "나만의 AI 비서 데이터 서버"로 표시된다
mcp = MCPServer("나만의 AI 비서 데이터 서버")


@mcp.tool()
def get_data_summary() -> dict:
    """
    저장된 시계열 데이터의 요약 정보(기간, 개수, 평균, 최댓값, 최솟값, 최근 추세)를 반환한다.
    데이터 전체를 훑어보고 싶을 때 가장 먼저 호출하면 좋은 도구.
    """
    items = firestore_service.list_data_items()
    return summary_service.calculate_summary(items)


@mcp.tool()
def get_data_in_range(start_date: str, end_date: str) -> list[dict]:
    """
    지정한 기간(start_date~end_date, YYYY-MM-DD 형식)의 개별 데이터를 반환한다.
    특정 날짜의 실제 값이 필요할 때 사용한다.
    """
    return firestore_service.get_data_in_range(start_date, end_date)


@mcp.tool()
def list_recent_conversations(limit: int = 5) -> list[dict]:
    """최근 대화 목록을 최신순으로 limit개 반환한다 (메시지 내용은 제외, 제목/날짜만)."""
    conversations = firestore_service.list_conversations()
    return conversations[:limit]


if __name__ == "__main__":
    # `python mcp_server.py`로 직접 실행하면 표준 MCP stdio 서버로 뜬다
    # (Claude Desktop 같은 클라이언트가 이 방식으로 연결한다)
    mcp.run()