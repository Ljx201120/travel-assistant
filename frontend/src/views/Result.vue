<template>
  <div class="page-wrapper">
    <!-- 数据无效时显示错误提示 -->
    <div v-if="!tripPlan" class="error-placeholder">
      <a-result status="error" title="行程加载失败" sub-title="未能获取有效的行程数据，请返回上一页重新生成">
        <template #extra>
          <a-button type="primary" @click="goBack">返回上一页</a-button>
        </template>
      </a-result>
    </div>

    <template v-else>
      <!-- 侧边导航 -->
      <div class="side-nav">
        <div class="nav-title">📍 快速导航</div>
        <div
          v-for="item in navItems"
          :key="item.key"
          class="nav-item"
          :class="{ active: activeSection[0] === item.key }"
          @click="scrollToSection({ key: item.key })"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="result-container">
        <div id="trip-plan-content" class="trip-plan-content">

          <!-- 行程概览 -->
          <div id="overview">
            <a-card class="section-card" title="✈️ 行程概览">
              <template #extra>
                <div v-if="!editMode" style="display: flex; gap: 8px">
                  <a-button type="primary" @click="toggleEditMode">✏️ 编辑行程</a-button>
                  <a-button @click="exportAsImage" :loading="exportLoading.image">📸 导出图片</a-button>
                  <a-button @click="exportAsPDF" :loading="exportLoading.pdf">📄 导出 PDF</a-button>
                </div>
                <div v-else style="display: flex; gap: 8px">
                  <a-button type="primary" @click="saveEdit">✅ 保存</a-button>
                  <a-button @click="cancelEdit">❌ 取消</a-button>
                </div>
              </template>
              <a-descriptions :column="3">
                <a-descriptions-item label="目的地">{{ tripPlan.city }}</a-descriptions-item>
                <a-descriptions-item label="出发日期">{{ tripPlan.start_date }}</a-descriptions-item>
                <a-descriptions-item label="返回日期">{{ tripPlan.end_date }}</a-descriptions-item>
                <a-descriptions-item label="总天数">{{ tripPlan.days?.length || 0 }} 天</a-descriptions-item>
              </a-descriptions>
              <p style="margin-top: 12px">{{ tripPlan.overall_suggestions }}</p>
            </a-card>
          </div>

          <!-- 天气信息 -->
          <div id="weather">
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
          </div>

          <!-- 预算明细 -->
          <div id="budget">
            <a-card v-if="tripPlan.budget" class="section-card" title="💰 预算明细">
              <a-descriptions :column="2">
                <a-descriptions-item label="景点门票">¥{{ tripPlan.budget.total_attractions }}</a-descriptions-item>
                <a-descriptions-item label="酒店住宿">¥{{ tripPlan.budget.total_hotels }}</a-descriptions-item>
                <a-descriptions-item label="餐饮费用">¥{{ tripPlan.budget.total_meals }}</a-descriptions-item>
                <a-descriptions-item label="交通费用">¥{{ tripPlan.budget.total_transportation }}</a-descriptions-item>
              </a-descriptions>
              <a-divider />
              <p style="font-size: 16px; font-weight: bold">总计：¥{{ tripPlan.budget.total }}</p>
            </a-card>
          </div>

          <!-- 地图可视化 -->
          <div id="map">
            <a-card class="section-card" title="🗺️ 地图可视化">
              <div id="amap-container" style="width: 100%; height: 500px; position: relative" />
            </a-card>
          </div>

          <!-- 每日行程详情 -->
          <div id="days">
            <a-card class="section-card" title="📅 每日行程详情">
              <a-collapse v-model:activeKey="activeKeys">
                <a-collapse-panel
                  v-for="day in tripPlan.days"
                  :key="String(day.day_index)"
                  :header="`第 ${day.day_index + 1} 天 · ${day.date}`"
                >
                  <p>{{ day.description }}</p>
                  <p>🚌 交通：{{ day.transportation }} &nbsp; 🏨 住宿：{{ day.accommodation }}</p>

                  <div v-if="day.hotel" style="margin-top: 12px">
                    <a-tag color="blue">酒店</a-tag>
                    <span>{{ day.hotel.name }} · {{ day.hotel.price_range }} · ⭐{{ day.hotel.rating }}</span>
                  </div>

                  <a-divider orientation="left">景点</a-divider>
                  <a-list :data-source="day.attractions" item-layout="horizontal">
                    <template #renderItem="{ item: attraction, index }">
                      <a-list-item v-if="attraction">
                        <a-list-item-meta>
                          <template #avatar>
                            <a-avatar>{{ index + 1 }}</a-avatar>
                          </template>
                          <template #title>{{ attraction.name }}</template>
                          <template #description>
                            {{ attraction.address }} · ⏱ {{ attraction.visit_duration }} 分钟
                            · 🎫 ¥{{ attraction.ticket_price ?? 0 }}
                          </template>
                        </a-list-item-meta>
                        <template #extra>
                          <img
                            v-if="attraction.image_url && !editMode"
                            :src="attraction.image_url"
                            style="width: 120px; height: 80px; object-fit: cover; border-radius: 4px"
                          />
                          <div v-if="editMode" style="display: flex; flex-direction: column; gap: 4px">
                            <a-button size="small" :disabled="index === 0" @click="moveUp(day.day_index, index)">⬆️ 上移</a-button>
                            <a-button size="small" :disabled="index === (day.attractions?.length || 0) - 1" @click="moveDown(day.day_index, index)">⬇️ 下移</a-button>
                            <a-button size="small" danger @click="removeAttraction(day.day_index, index)">🗑️ 删除</a-button>
                          </div>
                        </template>
                      </a-list-item>
                    </template>
                  </a-list>

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

        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import type { TripPlan, Attraction } from '@/types'

const router = useRouter()

function sanitizeTripPlan(plan: TripPlan): TripPlan {
  if (!plan.days) return plan
  plan.days.forEach(day => {
    if (Array.isArray(day.attractions)) {
      day.attractions = day.attractions.filter(
        (att): att is Attraction => att != null && typeof att === 'object'
      )
    }
  })
  return plan
}

let initialPlan: TripPlan | null = null
try {
  const raw = history.state?.tripPlan
  if (raw) {
    const parsed = JSON.parse(raw)
    if (parsed) initialPlan = sanitizeTripPlan(parsed)
  }
} catch (e) {
  console.error('解析行程数据失败', e)
  message.error('行程数据格式错误')
}
const tripPlan = ref<TripPlan | null>(initialPlan)

const activeKeys = ref<string[]>([])
watchEffect(() => {
  if (tripPlan.value?.days) {
    activeKeys.value = tripPlan.value.days.map(day => String(day.day_index))
  }
})

// 侧边导航
const navItems = [
  { key: 'overview', icon: '📋', label: '行程概览' },
  { key: 'weather', icon: '🌤️', label: '天气信息' },
  { key: 'budget', icon: '💰', label: '预算明细' },
  { key: 'map', icon: '🗺️', label: '地图' },
  { key: 'days', icon: '📅', label: '每日行程' },
]
const activeSection = ref(['overview'])

const scrollToSection = ({ key }: { key: string }) => {
  activeSection.value = [key]
  const element = document.getElementById(key)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const sectionIds = ['overview', 'weather', 'budget', 'map', 'days']
const handleScroll = () => {
  for (const id of [...sectionIds].reverse()) {
    const el = document.getElementById(id)
    if (el && el.getBoundingClientRect().top <= 80) {
      activeSection.value = [id]
      break
    }
  }
}
onMounted(() => window.addEventListener('scroll', handleScroll))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))

const editMode = ref(false)
const originalPlan = ref<TripPlan | null>(null)
const exportLoading = ref({ image: false, pdf: false })

let mapInstance: any = null
const mapLoaded = ref(false)

function assertPlan(): TripPlan {
  if (!tripPlan.value) throw new Error('行程数据不存在')
  return tripPlan.value
}

const toggleEditMode = () => {
  editMode.value = true
  originalPlan.value = JSON.parse(JSON.stringify(assertPlan()))
}

const saveEdit = () => {
  editMode.value = false
  originalPlan.value = null
  message.success('行程已保存')
}

const cancelEdit = () => {
  if (originalPlan.value) tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
  editMode.value = false
  originalPlan.value = null
  message.info('已取消编辑')
}

const removeAttraction = (dayIndex: number, attractionIndex: number) => {
  const plan = tripPlan.value
  if (!plan) return
  const day = plan.days?.[dayIndex]
  if (!day || !day.attractions) return
  day.attractions.splice(attractionIndex, 1)
  day.attractions = day.attractions.filter(att => att != null)
}

const moveUp = (dayIndex: number, attractionIndex: number) => {
  const attractions = tripPlan.value?.days?.[dayIndex]?.attractions
  if (!attractions || attractionIndex === 0) return
  ;[attractions[attractionIndex - 1], attractions[attractionIndex]] = [attractions[attractionIndex] as Attraction, attractions[attractionIndex - 1] as Attraction]
}

const moveDown = (dayIndex: number, attractionIndex: number) => {
  const attractions = tripPlan.value?.days?.[dayIndex]?.attractions
  if (!attractions || attractionIndex === attractions.length - 1) return
  ;[attractions[attractionIndex], attractions[attractionIndex + 1]] = [attractions[attractionIndex + 1] as Attraction, attractions[attractionIndex] as Attraction]
}

const goBack = () => router.back()

function getStaticMapUrl(
  center: [number, number],
  locations: Array<{ lng: number; lat: number }>
): string {
  const key = import.meta.env.VITE_AMAP_STATIC_KEY
  let url = `https://restapi.amap.com/v3/staticmap?key=${key}&size=600x400&zoom=12&location=${center[0]},${center[1]}`
  if (locations.length > 0) {
    const markers = locations.map(loc => `${loc.lng},${loc.lat}`).join('|')
    url += `&markers=mid,0xFF0000,A:${markers}`
  }
  return url
}

let originalMapInnerHTML: string | null = null

const replaceMapWithStaticImage = (): Promise<boolean> => {
  return new Promise(async (resolve) => {
    const mapContainer = document.getElementById('amap-container')
    if (!mapContainer || !tripPlan.value) { resolve(false); return }

    originalMapInnerHTML = mapContainer.innerHTML

    const locations: Array<{ lng: number; lat: number }> = []
    tripPlan.value.days.forEach(day => {
      day.attractions?.forEach(att => {
        if (att?.location) locations.push({ lng: att.location.longitude, lat: att.location.latitude })
      })
    })

    let center: [number, number] = [116.397128, 39.916527]
    if (locations.length > 0 && locations[0]) center = [locations[0].lng, locations[0].lat]

    const staticUrl = `/api/image-proxy?url=${encodeURIComponent(getStaticMapUrl(center, locations))}`

    mapContainer.innerHTML = ''
    const img = document.createElement('img')
    img.src = staticUrl
    img.crossOrigin = 'anonymous'
    img.style.width = '100%'
    img.style.height = '100%'
    img.style.objectFit = 'cover'
    img.style.display = 'block'

    img.onload = () => resolve(true)
    img.onerror = () => resolve(false)
    mapContainer.appendChild(img)
  })
}

const restoreDynamicMap = () => {
  const mapContainer = document.getElementById('amap-container')
  if (!mapContainer || originalMapInnerHTML === null) return
  mapContainer.innerHTML = originalMapInnerHTML
  originalMapInnerHTML = null
  if (mapInstance && typeof mapInstance.resize === 'function') mapInstance.resize()
}

const exportAsImage = async () => {
  if (!tripPlan.value) { message.error('无行程数据'); return }
  exportLoading.value.image = true
  try {
    if (!mapLoaded.value) { message.warning('地图正在加载，请稍后再试'); return }
    const replaced = await replaceMapWithStaticImage()
    if (!replaced) message.warning('静态地图生成失败，导出的图片可能不包含地图')
    await new Promise(resolve => setTimeout(resolve, 800))
    const element = document.getElementById('trip-plan-content')
    if (!element) throw new Error('内容容器不存在')
    const canvas = await html2canvas(element, { backgroundColor: '#ffffff', scale: 2, useCORS: true, allowTaint: false, logging: false })
    const link = document.createElement('a')
    link.download = `${tripPlan.value.city}_旅行计划.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    message.success('导出图片成功')
  } catch (error) {
    message.error('导出图片失败：' + (error instanceof Error ? error.message : '未知错误'))
  } finally {
    restoreDynamicMap()
    exportLoading.value.image = false
  }
}

const exportAsPDF = async () => {
  if (!tripPlan.value) { message.error('无行程数据'); return }
  exportLoading.value.pdf = true
  try {
    if (!mapLoaded.value) { message.warning('地图正在加载，请稍后再试'); return }
    const replaced = await replaceMapWithStaticImage()
    if (!replaced) message.warning('静态地图生成失败，导出的 PDF 可能不包含地图')
    await new Promise(resolve => setTimeout(resolve, 800))
    const element = document.getElementById('trip-plan-content')
    if (!element) throw new Error('内容容器不存在')
    const canvas = await html2canvas(element, { backgroundColor: '#ffffff', scale: 2, useCORS: true, allowTaint: false })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgWidth = 210
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pdf.internal.pageSize.getHeight()
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pdf.internal.pageSize.getHeight()
    }
    pdf.save(`${tripPlan.value.city}_旅行计划.pdf`)
    message.success('导出 PDF 成功')
  } catch (error) {
    message.error('导出 PDF 失败：' + (error instanceof Error ? error.message : '未知错误'))
  } finally {
    restoreDynamicMap()
    exportLoading.value.pdf = false
  }
}

const initDynamicMap = async () => {
  const plan = tripPlan.value
  if (!plan) throw new Error('行程数据为空')
  const container = document.getElementById('amap-container')
  if (!container) throw new Error('地图容器不存在')

  await new Promise<void>((resolve) => {
    const check = () => {
      const rect = container.getBoundingClientRect()
      if (rect.width > 0 && rect.height > 0) resolve()
      else setTimeout(check, 100)
    }
    check()
  })

  const AMap = await AMapLoader.load({ key: import.meta.env.VITE_AMAP_KEY, version: '2.0' })

  let center: [number, number] = [116.397128, 39.916527]
  const firstAttraction = plan.days?.[0]?.attractions?.find(att => att != null)
  if (firstAttraction?.location) center = [firstAttraction.location.longitude, firstAttraction.location.latitude]

  const map = new AMap.Map('amap-container', { zoom: 12, center, viewMode: '2D' })

  plan.days?.forEach(day => {
    day.attractions?.forEach((attraction, idx) => {
      if (!attraction) return
      const marker = new AMap.Marker({
        position: [attraction.location.longitude, attraction.location.latitude],
        title: attraction.name,
        label: { content: `${idx + 1}`, direction: 'top' },
      })
      map.add(marker)
    })
  })

  map.on('complete', () => { mapLoaded.value = true })
  if (map.getZoom()) mapLoaded.value = true
  mapInstance = map
}

onMounted(async () => {
  if (!tripPlan.value) return
  try {
    await initDynamicMap()
  } catch (error) {
    console.error('动态地图初始化失败', error)
    message.error('地图加载失败')
    mapLoaded.value = true
  }
})
</script>

<style scoped>
.page-wrapper {
  display: flex;
  min-height: 100vh;
  background: #f5f5f5;
}

.side-nav {
  position: fixed;
  top: 80px;
  left: 24px;
  width: 140px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  padding: 12px 0;
  z-index: 100;
}

.nav-title {
  font-size: 12px;
  color: #999;
  padding: 0 16px 8px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
  font-size: 13px;
}

.nav-item:hover {
  background: #f5f7ff;
  color: #4f6ef7;
}

.nav-item.active {
  background: #f0f4ff;
  color: #4f6ef7;
  font-weight: 600;
  border-left: 3px solid #4f6ef7;
}

.nav-icon {
  font-size: 14px;
}

.nav-label {
  flex: 1;
}

.result-container {
  margin-left: 200px;
  max-width: 960px;
  width: 100%;
  padding: 24px;
}

.trip-plan-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.error-placeholder {
  margin-top: 80px;
  width: 100%;
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

#amap-container {
  min-height: 500px;
  background-color: #f5f5f5;
}
</style>