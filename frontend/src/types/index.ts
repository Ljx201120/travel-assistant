export interface Location {
  longitude: number
  latitude: number
}

export interface Attraction {
  name: string
  address: string
  location: Location
  visit_duration: number
  description: string
  category?: string
  rating?: number
  image_url?: string | null
  ticket_price?: number
}

export interface TripPlan {
  city: string
  start_date: string
  end_date: string
  days: DayPlan[]
  weather_info: WeatherInfo[]
  overall_suggestions: string
  budget?: Budget
}

export interface TripPlanRequest {
  city: string
  start_date: string
  end_date: string
  days: number
  preferences: string
  budget: string
  transportation: string
  accommodation: string
}

export interface DayPlan {
  date: string;           // 日期
  day_index: number;      // 第几天(从0开始)
  description: string;    // 当日行程描述
  transportation: string; // 交通方式
  accommodation: string;  // 住宿安排
  hotel: Hotel | null;    // 酒店信息
  attractions: Attraction[]; // 景点列表
  meals: Meal[];          // 餐饮安排
}

export interface WeatherInfo {
  date: string;          // 日期
  day_weather: string;   // 白天天气
  night_weather: string; // 夜间天气
  day_temp: number;      // 白天温度(摄氏度)
  night_temp: number;    // 夜间温度(摄氏度)
  wind_direction: string; // 风向
  wind_power: string;    // 风力
}

export interface Budget {
  total_attractions: number; // 景点门票总费用
  total_hotels: number;      // 酒店总费用
  total_meals: number;       // 餐饮总费用
  total_transportation: number; // 交通总费用
  total: number;             // 总费用
}

export interface Hotel {
  name: string;           // 酒店名称
  address: string;        // 酒店地址
  location: Location | null; // 酒店位置
  price_range: string;    // 价格范围
  rating: string;         // 评分
  distance: string;       // 距离景点距离
  type: string;           // 酒店类型
  estimated_cost: number; // 预估费用(元/晚)
}

export interface Meal {
  type: string;              // 餐饮类型：breakfast/lunch/dinner/snack
  name: string;              // 餐饮名称
  address: string | null;    // 地址
  location: Location | null; // 经纬度坐标
  description: string | null; // 描述
  estimated_cost: number;    // 预估费用(元)
}