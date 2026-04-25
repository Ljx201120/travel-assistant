# tests/test_trip_integration.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.apis.trip import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# 真实请求体
request_data = {
    "city": "北京",
    "start_date": "2025-05-01",
    "end_date": "2025-05-02",
    "days": 2,
    "preferences": "历史文化",
    "budget": "中等",
    "transportation": "公共交通",
    "accommodation": "酒店",
}


@pytest.mark.integration
class TestTripIntegration:
    def test_create_trip_plan_returns_200(self):
        """完整链路：LLM + 高德 MCP + Unsplash，验证返回 200"""
        response = client.post("/plan", json=request_data)
        assert response.status_code == 200

    def test_create_trip_plan_structure(self):
        """验证返回数据结构符合 TripPlan 模型"""
        response = client.post("/plan", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["city"] == "北京"
        assert "days" in data
        assert isinstance(data["days"], list)
        assert len(data["days"]) > 0

        for day in data["days"]:
            assert "date" in day
            assert "attractions" in day
            assert isinstance(day["attractions"], list)

    def test_attractions_have_images(self):
        """验证 Unsplash 为每个景点填充了图片"""
        response = client.post("/plan", json=request_data)
        assert response.status_code == 200

        data = response.json()
        for day in data["days"]:
            for attraction in day["attractions"]:
                assert attraction["image_url"] is not None
                assert attraction["image_url"].startswith("https://")
