from src.core.services.unSplashService import UnsplashService

# 导入tripplan，tripplanrequest
from src.models.tripPlan import TripPlan, TripPlanRequest

# 导入fastapi
from fastapi import APIRouter
from src.core.agents.tripPlannerAgent import TripPlannerAgent

router = APIRouter()
unsplash_service = UnsplashService()
trip_planner_agent = TripPlannerAgent()


@router.post("/plan", response_model=TripPlan)
async def create_trip_plan(request: TripPlanRequest) -> TripPlan:
    # 生成旅行计划
    trip_plan = trip_planner_agent.plan_trip(request)

    # 为每个景点获取图片
    for day in trip_plan.days:
        for attraction in day.attractions:
            if not attraction.image_url:
                image_url = unsplash_service.get_photo_url(
                    f"{attraction.name} {trip_plan.city}"
                )
                attraction.image_url = image_url

    return trip_plan
