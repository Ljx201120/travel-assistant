<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { generateTripPlan } from '@/services/api'
import type { TripPlanRequest } from '@/types'
import dayjs, { Dayjs } from 'dayjs'

const router = useRouter()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')
const dateError = ref(false)
const dateRange = ref<[Dayjs, Dayjs] | null>(null)

const formData = ref<TripPlanRequest>({
  city: '',
  start_date: '',
  end_date: '',
  days: 3,
  preferences: '历史文化',
  budget: '中等',
  transportation: '公共交通',
  accommodation: '经济型酒店'
})

watch(dateRange, (val) => {
  if (val) {
    dateError.value = false
    formData.value.start_date = val[0].format('YYYY-MM-DD')
    formData.value.end_date = val[1].format('YYYY-MM-DD')
    formData.value.days = val[1].diff(val[0], 'day') + 1
  }
})

// const handleSubmit = async () => {
//   if (!dateRange.value) {
//     dateError.value = true
//     return
//   }
//   dateError.value = false

//   loading.value = true
//   loadingProgress.value = 0

//   const progressInterval = setInterval(() => {
//     if (loadingProgress.value < 90) {
//       loadingProgress.value += 10
//       if (loadingProgress.value <= 30) loadingStatus.value = '🔍 正在搜索景点...'
//       else if (loadingProgress.value <= 50) loadingStatus.value = '🌤️ 正在查询天气...'
//       else if (loadingProgress.value <= 70) loadingStatus.value = '🏨 正在推荐酒店...'
//       else loadingStatus.value = '📋 正在生成行程计划...'
//     }
//   }, 500)

//   try {
//     const response = await generateTripPlan(formData.value)
//     clearInterval(progressInterval)
//     loadingProgress.value = 100
//     router.push({ name: 'result', state: { tripPlan: JSON.stringify(response) } })
//   } catch (error) {
//     clearInterval(progressInterval)
//     loading.value = false
//     message.error('生成计划失败，请重试')
//   }
// }
const handleSubmit = async () => {
  if (!dateRange.value) {
    dateError.value = true
    return
  }
  dateError.value = false

  loading.value = true
  loadingProgress.value = 0

  const progressInterval = setInterval(() => {
    const current = loadingProgress.value
    if (current < 30) {
      loadingProgress.value += 10
      loadingStatus.value = '🔍 正在搜索景点...'
    } else if (current < 50) {
      loadingProgress.value += 8
      loadingStatus.value = '🌤️ 正在查询天气...'
    } else if (current < 70) {
      loadingProgress.value += 6
      loadingStatus.value = '🏨 正在推荐酒店...'
    } else if (current < 90) {
      loadingProgress.value += 4
      loadingStatus.value = '📋 正在生成行程计划...'
    } else if (current < 99) {
      loadingProgress.value += 1  // 90%-99% 非常慢
      loadingStatus.value = '⏳ 即将完成，请稍候...'
    }
    // 99% 停住等后端
  }, 500)

  try {
    const response = await generateTripPlan(formData.value)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    router.push({ name: 'result', state: { tripPlan: JSON.stringify(response) } })
  } catch (error) {
    clearInterval(progressInterval)
    loading.value = false
    message.error('生成计划失败，请重试')
  }
}
</script>

<template>
  <div class="home-container">
    <div class="page-header">
      <h1 class="page-title">✈️ 智能旅行助手</h1>
      <p class="page-subtitle">基于 AI 的个性化旅行规划</p>
    </div>

    <a-card class="form-card">
      <a-form
        :model="formData"
        layout="vertical"
        @finish="handleSubmit"
      >
        <!-- 目的地 -->
        <a-form-item
          label="目的地城市"
          name="city"
          :rules="[{ required: true, message: '请输入目的地城市' }]"
        >
          <a-input
            v-model:value="formData.city"
            placeholder="如：北京、上海、成都"
            size="large"
            allow-clear
          />
        </a-form-item>

        <!-- 出行日期 — 不用 name/rules，手动校验 -->
        <a-form-item label="出行日期">
          <a-range-picker
            v-model:value="dateRange"
            :disabled-date="(d: Dayjs) => d.isBefore(dayjs(), 'day')"
            format="YYYY-MM-DD"
            size="large"
            style="width: 100%"
          />
          <div v-if="dateError" style="color: #ff4d4f; font-size: 14px; margin-top: 4px;">
            请选择出行日期
          </div>
        </a-form-item>

        <!-- 旅行天数 -->
        <a-form-item label="旅行天数">
          <a-input-number
            v-model:value="formData.days"
            :min="1"
            :max="30"
            size="large"
            style="width: 100%"
            addon-after="天"
            :disabled="!!dateRange"
          />
        </a-form-item>

        <!-- 旅行偏好 -->
        <a-form-item label="旅行偏好">
          <a-select v-model:value="formData.preferences" size="large">
            <a-select-option value="历史文化">🏛️ 历史文化</a-select-option>
            <a-select-option value="自然风光">🌿 自然风光</a-select-option>
            <a-select-option value="美食探索">🍜 美食探索</a-select-option>
            <a-select-option value="购物娱乐">🛍️ 购物娱乐</a-select-option>
            <a-select-option value="亲子游">👨‍👩‍👧 亲子游</a-select-option>
            <a-select-option value="休闲度假">🏖️ 休闲度假</a-select-option>
          </a-select>
        </a-form-item>

        <!-- 预算 & 交通 -->
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="预算等级">
              <a-select v-model:value="formData.budget" size="large">
                <a-select-option value="经济">💰 经济</a-select-option>
                <a-select-option value="中等">💰💰 中等</a-select-option>
                <a-select-option value="豪华">💰💰💰 豪华</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="交通方式">
              <a-select v-model:value="formData.transportation" size="large">
                <a-select-option value="公共交通">🚇 公共交通</a-select-option>
                <a-select-option value="自驾">🚗 自驾</a-select-option>
                <a-select-option value="打车">🚕 打车</a-select-option>
                <a-select-option value="步行为主">🚶 步行为主</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 住宿类型 -->
        <a-form-item label="住宿类型">
          <a-radio-group v-model:value="formData.accommodation" size="large">
            <a-radio-button value="经济型酒店">经济型</a-radio-button>
            <a-radio-button value="舒适型酒店">舒适型</a-radio-button>
            <a-radio-button value="豪华酒店">豪华</a-radio-button>
            <a-radio-button value="民宿">民宿</a-radio-button>
          </a-radio-group>
        </a-form-item>

        <!-- 提交按钮 -->
        <a-form-item style="margin-top: 8px;">
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            block
          >
            {{ loading ? '规划中...' : '🚀 开始规划' }}
          </a-button>
        </a-form-item>

        <!-- 加载进度 -->
        <a-form-item v-if="loading">
          <a-progress :percent="loadingProgress" status="active" />
          <p style="text-align: center; margin-top: 8px; color: #666;">{{ loadingStatus }}</p>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 16px;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 36px;
  font-weight: bold;
  color: #fff;
  margin: 0;
}

.page-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 8px;
}

.form-card {
  width: 100%;
  max-width: 560px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}
</style>