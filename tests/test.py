# tests/test_trip_planner.py
from src.core.agents.tripPlannerAgent import TripPlannerAgent
from src.core.models.tripPlan import TripPlanRequest
from datetime import date


def test_full_trip_plan():
    print("=== 测试完整旅行规划 ===")

    # 构造请求
    request = TripPlanRequest(
        city="上海",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 6),
        days=5,
        preferences="历史文化",
        budget="中等",
        transportation="公共交通",
        accommodation="酒店",
    )

    # 运行规划
    planner = TripPlannerAgent()

    print("步骤1: 景点搜索...")
    print("步骤2: 天气查询...")
    print("步骤3: 酒店推荐...")
    print("步骤4: 生成行程...")

    result = planner.plan_trip(request)
    print("\n=== 规划结果 ===")
    print(result)


if __name__ == "__main__":
    test_full_trip_plan()
# src/core/agents/test.py
# from src.core.tools.mcpClient import AmapMCPClient
# from src.core.agents.simpleAgent import SimpleAgent
# from src.core.agents.attractionSearchAgent import ATTRACTION_AGENT_PROMPT
# from src.core.agents.weatherQueryAgent import WEATHER_AGENT_PROMPT
# from dotenv import load_dotenv

# def test_amap_direct():
#     """测试 MCP 直连"""
#     print("=== 测试 MCP 直连 ===")
#     load_dotenv()
#     amap = AmapMCPClient()
#     amap.start()
#     result = amap.call_tool("maps_text_search", {"keywords": "景点", "city": "北京"})
#     print(result)

# def test_attraction_agent():
#     """测试景点 agent"""
#     print("\n=== 测试景点 Agent ===")
#     load_dotenv()
#     amap = AmapMCPClient()
#     amap.start()
#     agent = SimpleAgent(name="景点搜索", prompt=ATTRACTION_AGENT_PROMPT, mcp_client=amap)
#     result = agent.run("请搜索北京的历史文化景点")
#     print(result)

# def test_weather_agent():
#     """测试天气 agent"""
#     print("\n=== 测试天气 Agent ===")
#     load_dotenv()
#     amap = AmapMCPClient()
#     amap.start()
#     agent = SimpleAgent(name="天气查询", prompt=WEATHER_AGENT_PROMPT, mcp_client=amap)
#     result = agent.run("请查询北京的天气")
#     print(result)

# if __name__ == "__main__":
#     test_amap_direct()
#     test_attraction_agent()
#     test_weather_agent()
