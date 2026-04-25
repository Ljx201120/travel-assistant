# tests/test_trip_router.py
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, call

from src.core.apis.trip import router
from src.models.tripPlan import TripPlan
from src.models.dayPlan import DayPlan
from src.models.attraction import Attraction
from src.models.location import Location

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# 构造最小可用的 Attraction（image_url=None，等待被填充）
fake_attraction_1 = Attraction(
    name="故宫",
    address="北京市东城区景山前街4号",
    location=Location(longitude=116.3974, latitude=39.9163),
    visit_duration=180,
    description="明清两代皇宫",
    image_url=None,
    ticket_price=60,
)
fake_attraction_2 = Attraction(
    name="天坛",
    address="北京市东城区天坛东里甲1号",
    location=Location(longitude=116.4107, latitude=39.8822),
    visit_duration=120,
    description="明清两代祭天场所",
    image_url=None,
    ticket_price=30,
)

fake_day_plan = DayPlan(
    date="2024-10-01",
    day_index=0,
    description="第一天行程",
    transportation="地铁",
    accommodation="酒店",
    attractions=[fake_attraction_1, fake_attraction_2],
)

fake_trip_plan = TripPlan(
    city="北京",
    start_date="2024-10-01",
    end_date="2024-10-01",
    days=[fake_day_plan],
    overall_suggestions="提前预订门票",
)

fake_request_data = {
    "city": "北京",
    "start_date": "2024-10-01",
    "end_date": "2024-10-01",
    "days": 1,
    "preferences": "",
    "budget": "中等",
    "transportation": "公共交通",
    "accommodation": "酒店",
}

fake_unsplash_url = "https://images.unsplash.com/photo-123456"


class TestTripPlan:
    @patch("src.core.apis.trip.trip_planner_agent")
    @patch("src.core.apis.trip.unsplash_service")
    def test_create_trip_plan_adds_images(self, mock_unsplash, mock_agent):
        """正常流程：景点没有图片时，应为每个景点填充 unsplash 图片"""
        mock_agent.plan_trip.return_value = fake_trip_plan
        mock_unsplash.get_photo_url.return_value = fake_unsplash_url

        response = client.post("/plan", json=fake_request_data)

        assert response.status_code == 200

        data = response.json()
        for day in data["days"]:
            for attraction in day["attractions"]:
                assert attraction["image_url"] == fake_unsplash_url

        assert mock_unsplash.get_photo_url.call_args_list == [
            call("故宫 北京"),
            call("天坛 北京"),
        ]

    @patch("src.core.apis.trip.trip_planner_agent")
    @patch("src.core.apis.trip.unsplash_service")
    def test_skips_image_if_already_set(self, mock_unsplash, mock_agent):
        """景点已有图片时，不应调用 unsplash"""
        attraction_with_image = fake_attraction_1.model_copy(
            update={"image_url": "https://already-set.com/img.jpg"}
        )
        plan_with_image = TripPlan(
            city="北京",
            start_date="2024-10-01",
            end_date="2024-10-01",
            days=[
                DayPlan(
                    date="2024-10-01",
                    day_index=0,
                    description="第一天行程",
                    transportation="地铁",
                    accommodation="酒店",
                    attractions=[attraction_with_image],
                )
            ],
            overall_suggestions="提前预订门票",
        )
        mock_agent.plan_trip.return_value = plan_with_image

        response = client.post("/plan", json=fake_request_data)

        assert response.status_code == 200
        mock_unsplash.get_photo_url.assert_not_called()
