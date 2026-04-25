from pydantic import BaseModel, Field
from typing import Optional, List
from .budget import Budget
from .dayPlan import DayPlan
from .weatherInfo import WeatherInfo
from datetime import date


class TripPlanRequest(BaseModel):
    """旅行规划请求"""

    city: str = Field(..., description="目的地城市")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    days: int = Field(..., description="旅行天数")
    preferences: str = Field(default="", description="旅行偏好")
    budget: str = Field(default="中等", description="预算等级")
    transportation: str = Field(default="公共交通", description="交通方式")
    accommodation: str = Field(default="酒店", description="住宿类型")


class TripPlan(BaseModel):
    """旅行计划"""

    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    days: List[DayPlan] = Field(default_factory=list, description="每日行程")
    weather_info: List[WeatherInfo] = Field(
        default_factory=list, description="天气信息"
    )
    overall_suggestions: str = Field(..., description="总体建议")
    budget: Optional[Budget] = Field(default=None, description="预算信息")
