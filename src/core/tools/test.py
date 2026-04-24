import os
from dotenv import load_dotenv
from mcpClient import AmapMCPClient

load_dotenv()

amap = AmapMCPClient(api_key=os.getenv("AMAP_MAPS_API_KEY"))

# 直接调用工具
result = amap.run(
    tool_name="maps_text_search", arguments={"keywords": "景点", "city": "北京"}
)
print(result)
# 临时测试脚本，列出所有可用工具
# import asyncio
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client

# async def list_tools():
#     server_params = StdioServerParameters(
#         command="npx",
#         args=["-y", "@amap/amap-maps-mcp-server"],
#         env={"AMAP_MAPS_API_KEY": "你的key"},
#     )
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
#             tools = await session.list_tools()
#             for tool in tools.tools:
#                 print(f"工具名: {tool.name}")
#                 print(f"描述: {tool.description}")
#                 print(f"参数: {tool.inputSchema}")
#                 print("---")

# asyncio.run(list_tools())
