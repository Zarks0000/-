﻿<template>
  <div class="h-full app-page relative flex flex-col pb-6">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">历史回顾</h1>
      <button @click="load" class="app-header-pill-button bg-emerald-50 text-xs text-emerald-700 font-bold">刷新</button>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-3">
      <div
        v-for="item in history"
        :key="item.route_id"
        class="app-card rounded-2xl p-4"
      >
        <div class="flex justify-between items-start">
          <h3 class="text-sm font-bold text-slate-800">{{ item.route_name }}</h3>
          <span class="text-[10px] text-slate-400">{{ item.end_date || '已完成' }}</span>
        </div>
        <div class="text-xs text-slate-500 mt-2">
          {{ item.origin_name }} → {{ item.dest_name }}
        </div>
        <div class="text-xs text-slate-500 mt-1">
          {{ (item.total_distance / 1000).toFixed(1) }} km · {{ item.days || 0 }} 天
        </div>
      </div>

      <div v-if="history.length === 0" class="text-center text-slate-400 text-sm py-16">
        暂无已完成摩旅行程
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { api } from '@/api'
import { showError } from '@/utils/uni'

type HistoryItem = {
  route_id: string
  route_name: string
  origin_name: string
  dest_name: string
  total_distance: number
  end_date: string
  days: number
}


const history = ref<HistoryItem[]>([])

const load = async () => {
  const res = await api.getMyHistory()
  if (res.status === 'success') {
    history.value = Array.isArray(res.data) ? res.data : []
  } else {
    showError(res.message || '加载失败')
  }
}

onMounted(load)
</script>

