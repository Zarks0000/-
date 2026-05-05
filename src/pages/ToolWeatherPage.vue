﻿<template>
  <div class="h-full app-page flex flex-col relative">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex items-center justify-between sticky top-0 z-50 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">天气查询</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-5">
      <div class="app-card rounded-2xl p-4">
        <label class="block text-sm font-medium text-slate-700 mb-2">输入查询城市</label>
        <input
          v-model="city"
          @keyup.enter="search"
          type="text"
          placeholder-class="app-input-placeholder"
          placeholder="例如: 三亚"
          class="app-input w-full bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
        >
        <div class="mt-3">
          <div class="flex items-center justify-between mb-2">
            <label class="block text-sm font-medium text-slate-700">查询日期</label>
            <button
              v-if="queryDate"
              @click="clearQueryDate"
              class="app-action-button m-0 p-0 bg-transparent border-0 rounded-none shadow-none text-xs text-slate-400"
            >
              清除
            </button>
          </div>
          <picker
            mode="date"
            :value="queryDate || todayDate"
            :start="todayDate"
            :end="weatherMaxDate"
            @change="onQueryDateChange"
          >
            <view
              class="app-input w-full bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm flex items-center justify-between"
              :class="queryDate ? 'text-slate-700' : 'text-slate-400'"
            >
              <text>{{ queryDate || '不选择则查询当前实时天气' }}</text>
              <Icon name="calendar" size="28rpx" class="shrink-0 ml-2" />
            </view>
          </picker>
          <p class="text-[10px] text-slate-400 mt-1">可选择未来 7 天内日期；清除后查询当前实时天气</p>
        </div>
        <button
          @click="search"
          :disabled="loading"
          class="app-full-button w-full mt-4 bg-[#064e3b] text-white py-3 rounded-xl text-sm font-bold shadow-sm active:scale-95 transition-transform disabled:opacity-50"
        >
          {{ loading ? '查询中...' : '查询' }}
        </button>
      </div>

      <div v-if="result" class="space-y-3">
        <!-- 实时天气模块 -->
        <div v-if="result.weather" class="bg-gradient-to-r from-sky-400 to-blue-500 rounded-2xl shadow-lg shadow-sky-500/20 p-5 text-white">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-sm opacity-90 mb-1">{{ city }}{{ result.weather.type === 'forecast' ? `${result.weather.date}天气预报` : '当前天气' }}</p>
              <h3 v-if="result.weather.type === 'forecast'" class="text-4xl font-bold font-mono">
                {{ result.weather.tempMin }}<span class="text-2xl">-</span>{{ result.weather.tempMax }}<span class="text-2xl">°C</span>
              </h3>
              <h3 v-else class="text-4xl font-bold font-mono">{{ result.weather.temp }}<span class="text-2xl">°C</span></h3>
            </div>
            <div class="text-right">
              <Icon name="cloud-sun" size="80rpx" class="brightness-0 invert" />
              <p class="font-medium">{{ result.weather.text }}</p>
            </div>
          </div>
          <div class="grid grid-cols-4 gap-2 mt-5 pt-4 border-t border-white/20 text-center">
            <div>
              <p class="text-[10px] opacity-80 mb-0.5">{{ result.weather.type === 'forecast' ? '白天/夜间' : '体感温度' }}</p>
              <p class="text-xs font-bold">
                {{ result.weather.type === 'forecast' ? `${result.weather.textDay}/${result.weather.textNight}` : `${result.weather.feelsLike}°C` }}
              </p>
            </div>
            <div>
              <p class="text-[10px] opacity-80 mb-0.5">风向风力</p>
              <p class="text-xs font-bold">{{ result.weather.windDir }} {{ result.weather.windScale }}级</p>
            </div>
            <div>
              <p class="text-[10px] opacity-80 mb-0.5">相对湿度</p>
              <p class="text-xs font-bold">{{ result.weather.humidity }}%</p>
            </div>
            <div>
              <p class="text-[10px] opacity-80 mb-0.5">能见度</p>
              <p class="text-xs font-bold">{{ result.weather.vis }}km</p>
            </div>
          </div>
        </div>
        <div v-if="result.weather && result.message" class="bg-slate-50 rounded-xl p-3 border border-slate-100">
          <p class="text-xs text-slate-600 leading-relaxed">{{ result.message }}</p>
        </div>
        <div v-else-if="result.message" class="bg-white rounded-xl p-4 text-center border border-slate-100">
          <p class="text-sm text-slate-500">{{ result.message }}</p>
        </div>

        <!-- 天气预警模块 -->
        <div v-if="(result.alerts || []).length > 0" class="mt-6">
          <h3 class="font-bold text-slate-800 mb-3 flex items-center text-sm">
            <Icon name="shield-alert" size="32rpx" class="mr-1 shrink-0" />
            <span>灾害预警</span>
          </h3>
          <div v-for="(alert, idx) in result.alerts" :key="idx" class="app-card rounded-2xl p-4 mb-3">
            <div class="flex items-center space-x-2 mb-2">
              <h3 class="font-bold text-slate-800 text-sm">{{ alert.title }}</h3>
            </div>
            <p class="text-sm text-slate-600 leading-relaxed">{{ alert.description }}</p>
            <p class="text-xs text-slate-400 mt-2">发布时间: {{ alert.time }}</p>
          </div>
        </div>
        <div v-else class="bg-emerald-50 rounded-xl p-4 text-center mt-4">
          <p class="text-sm text-emerald-600 font-medium">该地区当前无恶劣天气预警</p>
        </div>
      </div>

      <div v-else-if="searched && !loading" class="text-center text-slate-400 py-10">
        <p class="text-sm">未查询到该城市信息或网络异常</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { api } from '@/api'
import { showError } from '@/utils/uni'


const city = ref('')
const queryDate = ref('')
const loading = ref(false)
const searched = ref(false)
const result = ref<any>(null)

const formatPickerDate = (value: Date) => {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const todayDate = formatPickerDate(new Date())
const weatherMaxDate = formatPickerDate(new Date(Date.now() + 6 * 24 * 60 * 60 * 1000))

const onQueryDateChange = (event: any) => {
  queryDate.value = event?.detail?.value || ''
}

const clearQueryDate = () => {
  queryDate.value = ''
  result.value = null
}

const isValidDateText = (value: string) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const [year, month, day] = value.split('-').map(Number)
  const d = new Date(year, month - 1, day)
  return d.getFullYear() === year && d.getMonth() === month - 1 && d.getDate() === day
}

const search = async () => {
  if (!city.value.trim()) return
  const dateText = queryDate.value.trim()
  if (dateText && !isValidDateText(dateText)) {
    showError('日期格式请填写为 YYYY-MM-DD')
    return
  }
  loading.value = true
  searched.value = true
  try {
    const res = await api.getWeatherAlerts(city.value.trim(), dateText)
    if (res.status === 'ok' || res.status === 'success') {
      result.value = res
    } else {
      result.value = null
      showError(res.message || '天气查询失败')
    }
  } catch (e: any) {
    result.value = null
    showError(e.message || '天气查询失败，请确认后端服务已启动')
  } finally {
    loading.value = false
  }
}
</script>

