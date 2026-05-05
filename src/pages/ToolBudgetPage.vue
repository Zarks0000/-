﻿<template>
  <div class="h-full app-page flex flex-col relative">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex items-center justify-between sticky top-0 z-50 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">预算估算</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-5">
      <div class="app-card rounded-2xl p-4">
        <label class="block text-sm font-medium text-slate-700 mb-2">输入行程信息</label>
        <div class="space-y-3">
          <input 
            v-model="origin" 
            type="text" 
            placeholder-class="app-input-placeholder"
            placeholder="出发地，如：北京" 
            class="app-input w-full bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
          >
          <input 
            v-model="destination" 
            type="text" 
            placeholder-class="app-input-placeholder"
            placeholder="目的地，如：拉萨" 
            class="app-input w-full bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
          >
          <input
            v-model="viaCities"
            type="text"
            placeholder-class="app-input-placeholder"
            placeholder="途径城市，如：西安、兰州、西宁"
            class="app-input w-full bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
          >
          <input 
            v-model.number="days" 
            type="number" 
            placeholder-class="app-input-placeholder"
            placeholder="旅行天数，如：10" 
            class="app-input w-full bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
          >
          <textarea
            v-model="notes"
            rows="4"
            placeholder-class="app-textarea-placeholder"
            placeholder="备注（非必填），可补充同行人数、住宿偏好、是否高速优先、景点安排、车型油耗、预算风格等"
            class="app-textarea w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
          />
          <button 
            @click="estimate"
            :disabled="loading || !origin || !destination || !days"
            class="app-full-button w-full bg-[#064e3b] text-white px-5 py-3 rounded-xl text-sm font-bold shadow-sm active:scale-95 transition-transform disabled:opacity-50 mt-2"
          >
            {{ loading ? '正在估算' : '开始估算' }}
          </button>
        </div>
      </div>

      <div v-if="result" class="space-y-4">
        <div class="bg-[#064e3b] rounded-2xl p-5 text-white shadow-lg shadow-emerald-900/15 text-center">
          <p class="text-xs opacity-90 mb-1">预估总花费</p>
          <h3 class="text-4xl font-bold font-mono">¥ {{ result.data.total_cny }}</h3>
          <div class="bg-black/10 rounded-lg p-3 text-xs leading-relaxed text-left mt-4">
            <span class="font-bold mr-1">专家建议：</span>{{ result.data.advice }}
          </div>
        </div>

        <h3 class="font-bold text-slate-800 flex items-center">
          <Icon name="calculator" size="32rpx" class="mr-1 shrink-0" />
          <span>费用拆解</span>
        </h3>
        <div class="app-card rounded-2xl overflow-hidden divide-y divide-slate-50">
          <div class="p-3 flex justify-between items-center">
            <span class="text-sm font-medium text-slate-700">燃油费</span>
            <span class="text-sm font-bold font-mono text-slate-800">¥ {{ result.data.fuel_cny }}</span>
          </div>
          <div class="p-3 flex justify-between items-center">
            <span class="text-sm font-medium text-slate-700">住宿费</span>
            <span class="text-sm font-bold font-mono text-slate-800">¥ {{ result.data.accommodation_cny }}</span>
          </div>
          <div class="p-3 flex justify-between items-center">
            <span class="text-sm font-medium text-slate-700">餐饮费</span>
            <span class="text-sm font-bold font-mono text-slate-800">¥ {{ result.data.food_cny }}</span>
          </div>
          <div class="p-3 flex justify-between items-center">
            <span class="text-sm font-medium text-slate-700">其他费用</span>
            <span class="text-sm font-bold font-mono text-slate-800">¥ {{ result.data.other_cny }}</span>
          </div>
        </div>
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


const origin = ref('')
const destination = ref('')
const viaCities = ref('')
const days = ref<number | ''>('')
const notes = ref('')
const loading = ref(false)
const result = ref<any>(null)

const estimate = async () => {
  if (!origin.value || !destination.value || !days.value) return
  
  loading.value = true
  try {
    const res = await api.estimateBudget(
      origin.value,
      destination.value,
      Number(days.value),
      viaCities.value,
      notes.value
    )
    result.value = (res.status === 'ok' || res.status === 'success') ? res : null
  } catch (e: any) {
    showError(e.message || '大模型估算失败')
  } finally {
    loading.value = false
  }
}
</script>

