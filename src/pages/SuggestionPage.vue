﻿<template>
  <div class="h-full app-page flex flex-col relative">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex items-center justify-between sticky top-0 z-50 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">全部出行提醒</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8">
      <div v-if="currentRoute" class="mb-4 rounded-2xl bg-white border border-slate-100 shadow-sm p-4">
        <div class="text-[10px] text-slate-400 mb-1">当前行程</div>
        <div class="text-base font-bold text-slate-800 truncate">{{ currentRoute.name }}</div>
        <div class="mt-2 text-xs text-slate-500 truncate">
          {{ currentRoute.origin }} - {{ currentRoute.destination }}
        </div>
      </div>

      <section v-if="store.alerts.value.length > 0" class="space-y-3">
        <div
          v-for="(alert, index) in store.alerts.value"
          :key="alert.id || index"
          class="p-4 rounded-r-xl flex items-start gap-3 border-l-4 shadow-sm"
          :class="alertToneClass(alert)"
        >
          <Icon :name="alertIconName(alert)" size="40rpx" class="shrink-0 mt-0.5" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2">
              <h2 class="text-sm font-bold truncate" :class="alertTextClass(alert)">
                {{ alert.title || '出行提醒' }}
              </h2>
              <span class="shrink-0 rounded-full bg-white/70 px-2 py-0.5 text-[10px]" :class="alertTextClass(alert)">
                {{ alertLevelText(alert) }}
              </span>
            </div>
            <p class="mt-2 text-xs leading-relaxed" :class="alertTextClass(alert)">
              {{ alert.description || '暂无详细说明' }}
            </p>
          </div>
        </div>
      </section>

      <div v-else class="py-20 text-center text-slate-400">
        <Icon name="info" size="96rpx" />
        <p class="mt-3 text-sm">暂无出行提醒</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { useRouteStore } from '@/composables/useRouteStore'

const store = useRouteStore()
const currentRoute = computed(() => store.mainRoute.value)

const alertLevel = (alert: any) => alert?.severity || alert?.level || 'normal'

const alertToneClass = (alert: any) => {
  const level = alertLevel(alert)
  if (level === 'high') return 'bg-red-50 border-red-500'
  if (level === 'medium') return 'bg-emerald-50 border-emerald-500'
  if (level === 'low') return 'bg-blue-50 border-blue-500'
  return 'bg-slate-50 border-slate-400'
}

const alertTextClass = (alert: any) => {
  const level = alertLevel(alert)
  if (level === 'high') return 'text-red-900'
  if (level === 'medium') return 'text-emerald-900'
  if (level === 'low') return 'text-blue-900'
  return 'text-slate-900'
}

const alertIconName = (alert: any) => {
  if (alertLevel(alert) === 'high') return 'alert-triangle'
  if (alert?.type === 'weather') return 'cloud-snow'
  if (alert?.type === 'news') return 'book-open'
  if (alert?.type === 'restriction') return 'shield-alert'
  return 'wrench'
}

const alertLevelText = (alert: any) => {
  const level = alertLevel(alert)
  if (level === 'high') return '重要'
  if (level === 'medium') return '关注'
  if (level === 'low') return '提示'
  return '提醒'
}

const refreshAlerts = async () => {
  await store.fetchRoutes()
  if (currentRoute.value) {
    await store.fetchAlertsAndSuggestions(currentRoute.value)
  }
}

onShow(refreshAlerts)
</script>

