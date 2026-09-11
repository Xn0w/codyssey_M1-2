"""
mcp_client_test.py
-------------------
보너스 과제 검증용: "외부 채널/클라이언트"가 실제로 MCP 프로토콜을 통해
우리 도구를 호출하는 과정을 재현한 스크립트.

MCP Inspector(브라우저 화면)는 보안 설정(DNS 리바인딩 방지) 때문에
로컬 환경에서 막히는 경우가 있어서, 대신 파이썬으로 직접
"외부 클라이언트" 역할을 하는 코드를 짜서 검증한다.
Claude Desktop 같은 실제 클라이언트도 내부적으로는 이것과 똑같은
방식(stdio 프로토콜)으로 mcp_server.py에 연결해서 도구를 부른다.

실행 방법 (backend 폴더 안에서, 서버를 따로 켤 필요 없음 - 이 스크립트가 알아서 실행함):
    venv/bin/python mcp_client_test.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # "외부 클라이언트"가 mcp_server.py를 별도 프로세스로 띄워서 연결하는 부분.
    # 실제 Claude Desktop 등도 설정 파일에 이런 command/args를 등록해서 연결한다.
    params = StdioServerParameters(
        command=sys.executable,  # 지금 이 venv의 python을 그대로 사용
        args=["mcp_server.py"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1) 서버가 어떤 도구를 제공하는지 목록 조회
            tools = await session.list_tools()
            print("=== 사용 가능한 도구 목록 ===")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # 2) 실제로 도구 하나를 호출해본다 (요약 정보 조회)
            print("\n=== get_data_summary 호출 결과 ===")
            summary_result = await session.call_tool("get_data_summary", {})
            print(summary_result.content[0].text)

            # 3) 기간 조회 도구도 호출해본다
            print("\n=== get_data_in_range 호출 결과 (2026-07-15 ~ 2026-07-17) ===")
            range_result = await session.call_tool(
                "get_data_in_range",
                {"start_date": "2026-07-15", "end_date": "2026-07-17"},
            )
            print(range_result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())