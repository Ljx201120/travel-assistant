from pydantic import BaseModel, Field, field_validator
from typing import Optional
from .location import Location


class Meal(BaseModel):
    """餐饮信息"""

    type: str = Field(..., description="餐饮类型：breakfast/lunch/dinner/snack")
    name: str = Field(..., description="餐饮名称")
    address: Optional[str] = Field(default=None, description="地址")
    location: Optional[Location] = Field(default=None, description="经纬度坐标")
    description: Optional[str] = Field(default=None, description="描述")
    estimated_cost: int = Field(default=0, description="预估费用(元)")

    @field_validator("estimated_cost", mode="before")
    def parse_estimated_cost(cls, v):
        """解析预估费用字符串："100元" -> 100"""
        if isinstance(v, str):
            v = v.replace("元", "").replace("¥", "").replace("$", "").strip()
            try:
                return int(v)
            except ValueError:
                return 0  # 容错处理
        return v
