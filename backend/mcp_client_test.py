import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== 사용 가능한 도구 목록 ===")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            print("\n=== get_data_summary 호출 결과 ===")
            summary_result = await session.call_tool("get_data_summary", {})
            print(summary_result.content[0].text)

            print("\n=== get_data_in_range 호출 결과 (2026-07-15 ~ 2026-07-17) ===")
            range_result = await session.call_tool(
                "get_data_in_range",
                {"start_date": "2026-07-15", "end_date": "2026-07-17"},
            )
            print(range_result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
