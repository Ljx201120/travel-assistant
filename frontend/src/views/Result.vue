<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import type { TripPlan } from '@/types'

const tripPlan = ref<TripPlan>(JSON.parse(history.state.tripPlan))

onMounted(async () => {
  const AMap = await AMapLoader.load({
    key: import.meta.env.VITE_AMAP_KEY,
    version: '2.0'
  })
  const firstAttraction = tripPlan.value.days[0]?.attractions[0]
  const center: [number, number] = firstAttraction
    ? [firstAttraction.location.longitude, firstAttraction.location.latitude]
    : [116.397128, 39.916527]
  const map = new AMap.Map('amap-container', {
    zoom: 12,
    center: center
  })

  tripPlan.value.days.forEach((day) => {
    day.attractions.forEach((attraction, index) => {
      const marker = new AMap.Marker({
        position: [attraction.location.longitude, attraction.location.latitude],
        title: attraction.name,
        label: { content: `${index + 1}`, direction: 'top' }
      })
      map.add(marker)
    })
  })
})
</script>

<template>
  <div class="result-container">

    <!-- 行程概览 -->
    <a-card class="section-card" title="✈️ 行程概览">
      <a-descriptions :column="3">
        <a-descriptions-item label="目的地">{{ tripPlan.city }}</a-descriptions-item>
        <a-descriptions-item label="出发日期">{{ tripPlan.start_date }}</a-descriptions-item>
        <a-descriptions-item label="返回日期">{{ tripPlan.end_date }}</a-descriptions-item>
        <a-descriptions-item label="总天数">{{ tripPlan.days.length }} 天</a-descriptions-item>
      </a-descriptions>
      <p style="margin-top: 12px;">{{ tripPlan.overall_suggestions }}</p>
    </a-card>

    <!-- 天气信息 -->
    <a-card class="section-card" title="🌤️ 天气信息">
      <div class="weather-list">
        <a-card
          v-for="w in tripPlan.weather_info"
          :key="w.date"
          size="small"
          class="weather-item"
        >
          <p class="weather-date">{{ w.date }}</p>
          <p>白天：{{ w.day_weather }} {{ w.day_temp }}°C</p>
          <p>夜间：{{ w.night_weather }} {{ w.night_temp }}°C</p>
          <p>{{ w.wind_direction }} {{ w.wind_power }}</p>
        </a-card>
      </div>
    </a-card>

    <!-- 预算明细 -->
    <a-card v-if="tripPlan.budget" class="section-card" title="💰 预算明细">
      <a-descriptions :column="2">
        <a-descriptions-item label="景点门票">¥{{ tripPlan.budget.total_attractions }}</a-descriptions-item>
        <a-descriptions-item label="酒店住宿">¥{{ tripPlan.budget.total_hotels }}</a-descriptions-item>
        <a-descriptions-item label="餐饮费用">¥{{ tripPlan.budget.total_meals }}</a-descriptions-item>
        <a-descriptions-item label="交通费用">¥{{ tripPlan.budget.total_transportation }}</a-descriptions-item>
      </a-descriptions>
      <a-divider />
      <p style="font-size: 16px; font-weight: bold;">总计：¥{{ tripPlan.budget.total }}</p>
    </a-card>

    <!-- 地图可视化 -->
    <a-card class="section-card" title="🗺️ 地图可视化">
      <div id="amap-container" style="width: 100%; height: 500px;" />
    </a-card>

    <!-- 每日行程详情 -->
    <a-card class="section-card" title="📅 每日行程详情">
      <a-collapse>
        <a-collapse-panel
          v-for="day in tripPlan.days"
          :key="day.day_index"
          :header="`第 ${day.day_index + 1} 天 · ${day.date}`"
        >
          <p>{{ day.description }}</p>
          <p>🚌 交通：{{ day.transportation }} &nbsp; 🏨 住宿：{{ day.accommodation }}</p>

          <!-- 酒店 -->
          <div v-if="day.hotel" style="margin-top: 12px;">
            <a-tag color="blue">酒店</a-tag>
            <span>{{ day.hotel.name }} · {{ day.hotel.price_range }} · ⭐{{ day.hotel.rating }}</span>
          </div>

          <!-- 景点 -->
          <a-divider orientation="left">景点</a-divider>
          <a-list :data-source="day.attractions" item-layout="horizontal">
            <template #renderItem="{ item: attraction, index }">
              <a-list-item>
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar>{{ index + 1 }}</a-avatar>
                  </template>
                  <template #title>{{ attraction.name }}</template>
                  <template #description>
                    {{ attraction.address }} · ⏱ {{ attraction.visit_duration }} 分钟
                    · 🎫 ¥{{ attraction.ticket_price }}
                  </template>
                </a-list-item-meta>
                <template #extra>
                  <img
                    v-if="attraction.image_url"
                    :src="attraction.image_url"
                    style="width: 120px; height: 80px; object-fit: cover; border-radius: 4px;"
                  />
                </template>
              </a-list-item>
            </template>
          </a-list>

          <!-- 餐饮 -->
          <a-divider orientation="left">餐饮</a-divider>
          <a-list :data-source="day.meals" size="small">
            <template #renderItem="{ item: meal }">
              <a-list-item>
                <a-tag>{{ meal.type }}</a-tag>
                {{ meal.name }}
                <span v-if="meal.description"> · {{ meal.description }}</span>
                · ¥{{ meal.estimated_cost }}
              </a-list-item>
            </template>
          </a-list>

        </a-collapse-panel>
      </a-collapse>
    </a-card>

  </div>
</template>

<style scoped>
.result-container {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.weather-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.weather-item {
  min-width: 160px;
}

.weather-date {
  font-weight: bold;
  margin-bottom: 4px;
}
</style>