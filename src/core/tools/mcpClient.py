# src/core/tools/mcpClient.py
import asyncio
import os
import threading
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# parents[0]=tools, parents[1]=core, parents[2]=src, parents[3]=travel-assistant
load_dotenv(Path(__file__).parents[3] / ".env")


class AmapMCPClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("AMAP_MAPS_API_KEY")
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@amap/amap-maps-mcp-server"],
            env={"AMAP_MAPS_API_KEY": self.api_key},
        )
        self._session = None
        self._loop = asyncio.new_event_loop()
        self._ready = threading.Event()  # 用 Event 替代 sleep

    def start(self):
        thread = threading.Thread(target=self._run_loop, daemon=True)
        thread.start()
        # 等待连接真正就绪，最多等10秒
        if not self._ready.wait(timeout=10):
            raise RuntimeError("MCP Server 启动超时")

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._maintain_session())

    async def _maintain_session(self):
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self._session = session
                self._ready.set()  # 通知主线程连接就绪
                await asyncio.Event().wait()  # 保持连接

    def call_tool(self, tool_name: str, arguments: dict) -> str:
        if not self._session:
            raise RuntimeError("MCP Client 未启动，请先调用 start()")
        future = asyncio.run_coroutine_threadsafe(
            self._session.call_tool(tool_name, arguments=arguments),
            self._loop,
        )
        result = future.result(timeout=30)
        return result.content[0].text
