# src/core/agents/tripPlannerAgent.py
from src.core.agents.simpleAgent import SimpleAgent
from src.core.agents.attractionSearchAgent import ATTRACTION_AGENT_PROMPT
from src.core.agents.weatherQueryAgent import WEATHER_AGENT_PROMPT
from src.core.agents.hotelAgent import HOTEL_AGENT_PROMPT
from src.core.agents.plannerAgent import PLANNER_AGENT_PROMPT
from src.models.tripPlan import TripPlanRequest, TripPlan
from src.core.tools.mcpClient import AmapMCPClient


class TripPlannerAgent:
    def __init__(self):
        self.amap = AmapMCPClient()
        self.amap.start()
        self.attraction_agent = SimpleAgent(
            name="景点搜索", prompt=ATTRACTION_AGENT_PROMPT, mcp_client=self.amap
        )
        self.weather_agent = SimpleAgent(
            name="天气查询", prompt=WEATHER_AGENT_PROMPT, mcp_client=self.amap
        )
        self.hotel_agent = SimpleAgent(
            name="酒店推荐", prompt=HOTEL_AGENT_PROMPT, mcp_client=self.amap
        )
        self.planner_agent = SimpleAgent(
            name="行程规划", prompt=PLANNER_AGENT_PROMPT, mcp_client=self.amap
        )

    def plan_trip(self, request: TripPlanRequest) -> TripPlan:
        # 步骤1: 景点搜索
        attraction_response = self.attraction_agent.run(
            f"请搜索{request.city}的{request.preferences}景点"
        )

        # 步骤2: 天气查询
        weather_response = self.weather_agent.run(f"请查询{request.city}的天气")

        # 步骤3: 酒店推荐
        hotel_response = self.hotel_agent.run(
            f"请搜索{request.city}的{request.accommodation}酒店"
        )

        # 步骤4: 整合生成计划
        planner_query = self._build_planner_query(
            request, attraction_response, weather_response, hotel_response
        )
        planner_response = self.planner_agent.run(planner_query)

        # 步骤5: 解析JSON
        trip_plan = self._parse_trip_plan(planner_response)
        return trip_plan

    def _parse_trip_plan(self, response: str) -> TripPlan:
        import json
        import re

        response = response.strip()
        if not response:
            raise ValueError("Empty response")
        try:
            raw_data = json.loads(response)
        except json.JSONDecodeError:
            # 提取 ```json ... ``` 或最外层大括号
            match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
            if not match:
                match = re.search(r"(\{.*\})", response, re.DOTALL)
            if not match:
                raise ValueError(f"No JSON found in response: {response[:200]}")
            raw_data = json.loads(match.group(1))
        return TripPlan.model_validate(raw_data)

        # import re
        # import json
        # # 1. 去除首尾空白
        # response = response.strip()
        # if not response:
        #     raise ValueError("Response is empty")

        # # 2. 尝试直接解析
        # try:
        #     data = json.loads(response)
        # except json.JSONDecodeError:
        #     # 3. 如果失败，尝试提取 ```json ... ``` 块
        #     json_pattern = r"```json\s*(\{.*?\})\s*```"
        #     match = re.search(json_pattern, response, re.DOTALL)
        #     if match:
        #         json_str = match.group(1)
        #     else:
        #         # 4. 尝试提取任何 {...} 结构（非贪婪匹配最外层大括号）
        #         brace_pattern = r"(\{.*\})"
        #         match = re.search(brace_pattern, response, re.DOTALL)
        #         if not match:
        #             raise ValueError(f"Could not extract JSON from response: {response[:200]}...")
        #         json_str = match.group(1)
        #     data = json.loads(json_str)

        # # 5. 使用已定义的 Pydantic 模型进行映射（无需手动赋值）
        # return TripPlan.model_validate(data)

    def _build_planner_query(
        self,
        request: TripPlanRequest,
        attraction_response: str,
        weather_response: str,
        hotel_response: str,
    ) -> str:
        """构建规划Agent的查询"""
        return f"""
    请根据以下信息生成{request.city}的{request.days}日旅行计划:

    **用户需求:**
    - 目的地: {request.city}
    - 日期: {request.start_date} 至 {request.end_date}
    - 天数: {request.days}天
    - 偏好: {request.preferences}
    - 预算: {request.budget}
    - 交通方式: {request.transportation}
    - 住宿类型: {request.accommodation}

    **景点信息:**
    {attraction_response}

    **天气信息:**
    {weather_response}

    **酒店信息:**
    {hotel_response}

    请生成详细的旅行计划,包括每天的景点安排、餐饮推荐、住宿信息和预算明细。
    """
