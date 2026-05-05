﻿<template>
  <div class="h-full app-page relative flex flex-col pb-20">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">我的模板详情</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 space-y-4" v-if="data">
      <section class="app-card rounded-2xl p-4">
        <div class="flex items-start gap-3">
          <div class="w-11 h-11 rounded-xl bg-emerald-50 flex items-center justify-center shrink-0">
            <Icon name="file-text" size="40rpx" />
          </div>
          <div class="min-w-0 flex-1">
            <h2 class="text-lg font-bold text-slate-800 line-clamp-2">{{ data.title }}</h2>
            <p class="text-xs text-slate-500 leading-relaxed mt-2">{{ data.desc || '自定义摩旅模板' }}</p>
          </div>
        </div>
        <div class="mt-4 pt-4 border-t border-slate-100 flex">
          <div class="text-center flex-1 border-r border-slate-100">
            <div class="text-xs text-slate-400 mb-1">建议天数</div>
            <div class="font-bold text-slate-800">{{ data.days }} 天</div>
          </div>
          <div class="text-center flex-1">
            <div class="text-xs text-slate-400 mb-1">路书段数</div>
            <div class="font-bold text-slate-800">{{ data.schedule.length }} 段</div>
          </div>
        </div>
      </section>

      <section>
        <h3 class="font-bold text-slate-800 mb-3 flex items-center">
          <Icon name="map" size="32rpx" class="mr-1 shrink-0" />
          <span>分日路书参考</span>
        </h3>
        <div class="space-y-3">
          <div v-for="day in data.schedule" :key="day.day" class="app-card rounded-2xl p-4">
            <div class="flex justify-between items-center mb-2">
              <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded text-xs font-bold">Day {{ day.day }}</span>
              <span class="text-xs text-slate-400 font-medium">约 {{ day.distance_km }} km</span>
            </div>
            <h4 class="font-bold text-slate-800 text-sm mb-1">{{ day.title }}</h4>
            <p class="text-xs text-slate-500 leading-relaxed">{{ day.description }}</p>
          </div>
        </div>
      </section>
    </main>

    <div v-else class="flex-1 flex items-center justify-center text-slate-400">
      未找到该模板
    </div>

    <div class="fixed bottom-0 w-full md:w-[375px] bg-white border-t border-slate-100 p-4 pb-8 z-40">
      <button @click="applyTemplate" class="app-full-button w-full bg-[#064e3b] text-white font-bold py-3.5 rounded-xl shadow-lg shadow-[#064e3b]/30 active:scale-[0.98] transition-transform">
        套用此模板
      </button>
    </div>

    <CreateRouteModal
      ref="createRouteModalRef"
      :is-open="isCreateModalOpen"
      @close="isCreateModalOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { router } from '@/utils/router'
import { onLoad } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import { api } from '@/api'
import CreateRouteModal from '@/components/CreateRouteModal.vue'

type ScheduleItem = {
  day: number
  title: string
  distance_km: number
  description: string
}

type MyTemplate = {
  id: string
  title: string
  desc: string
  days: number
  schedule: ScheduleItem[]
}

const route = { params: {} as any, query: {} as any };

onLoad((options) => {
  route.params = options || {};
  route.query = options || {};
})

const data = ref<MyTemplate | null>(null)
const isCreateModalOpen = ref(false)
const createRouteModalRef = ref<InstanceType<typeof CreateRouteModal> | null>(null)

const normalize = (raw: any): MyTemplate => {
  const schedule = Array.isArray(raw?.schedule) && raw.schedule.length > 0
    ? raw.schedule.map((s: any, idx: number) => ({
        day: idx + 1,
        title: s?.title || `第${idx + 1}天行程`,
        distance_km: Number(s?.distance_km || 0),
        description: s?.description || '沿途骑行，按计划前往下一站。'
      }))
    : [{ day: 1, title: '第1天行程', distance_km: 0, description: raw?.desc || '待补充' }]
  return {
    id: raw?.id || '',
    title: raw?.title || '未命名模板',
    desc: raw?.desc || raw?.note || '',
    days: Math.max(1, Number(raw?.days || schedule.length || 1)),
    schedule
  }
}

const load = async () => {
  const id = route.params.id as string
  const res = await api.getMyTemplates()
  if (res.status !== 'success' || !Array.isArray(res.data)) return
  const found = res.data.find((x: any) => x.id === id)
  if (!found) return
  data.value = normalize(found)
}

const applyTemplate = () => {
  if (!data.value) return
  isCreateModalOpen.value = true
  setTimeout(() => {
    createRouteModalRef.value?.openWithPreset({
      name: data.value?.title || '我的模板',
      schedule: Array.isArray(data.value?.schedule) ? data.value.schedule : []
    })
  }, 50)
}

onMounted(load)
</script>

